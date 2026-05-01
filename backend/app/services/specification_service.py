from typing import List, Dict, Any, Optional
import re
from decimal import Decimal
from app.models.specification import SpecificationItem, CalculationType, CalculationDimension

class SpecificationService:
    @staticmethod
    def calculate_item_quantity(
        item: SpecificationItem, 
        parent_dimensions: Dict[str, Any]
    ) -> Decimal:
        """
        Calculates the quantity of a component based on smart rules.
        parent_dimensions should contain: 'width_mm', 'height_mm', 'length_mm', 'weight_kg', 'custom_attributes'
        """
        if not item.calc_type or item.calc_type == CalculationType.FIXED:
            return Decimal(str(item.quantity or 0))

        is_meters = item.unit_of_measure == 'м'
        w = float(parent_dimensions.get('width_mm') or 0)
        h = float(parent_dimensions.get('height_mm') or 0)
        l = float(parent_dimensions.get('length_mm') or 0)
        kg = float(parent_dimensions.get('weight_kg') or 0)
        custom_attrs = parent_dimensions.get('custom_attributes') or {}

        result = 0.0

        if item.calc_type == CalculationType.INTERPOLATION:
            result = SpecificationService._calculate_interpolation(item, w, h, l, custom_attrs)
        elif item.calc_type == CalculationType.PROPORTIONAL:
            dim_key = item.calc_dimension or 'width_mm'
            dim_val = float(parent_dimensions.get(dim_key) or 0)
            
            # Check for characteristic override
            config = item.calc_dim_config or {}
            dim_map = {'height_mm': 'h', 'width_mm': 'w', 'length_mm': 'l'}
            key = dim_map.get(dim_key, 'w')
            dim_config = config.get(key, {})
            
            unit = dim_config.get('unit', 'мм')
            char_name = dim_config.get('char_name')
            
            # Global Automation for Proportional
            if not char_name and item.specification and item.specification.product and item.specification.product.variant_config:
                vcfg = item.specification.product.variant_config
                dim_map_vcfg = {'height_mm': 'height', 'width_mm': 'width', 'length_mm': 'length'}
                g = vcfg.get(dim_map_vcfg.get(dim_key))
                if g and g.get('source') == 'attribute' and g.get('attr_id'):
                    potential_names = ['Розмір', 'Розмір (мм)', 'Size']
                    for p_name in potential_names:
                        if p_name in custom_attrs:
                            char_name = p_name
                            break

            if char_name and char_name in custom_attrs:
                dim_val = float(custom_attrs[char_name])
            
            coeff = float(item.calc_formula or 0)
            if is_meters:
                # If source is characteristic, use char unit. Else use mm.
                source_unit = unit if char_name else 'мм'
                meters = SpecificationService._to_meters(dim_val, source_unit)
                result = coeff * meters
            else:
                result = dim_val * coeff
                
            # Apply global waste for proportional
            waste_factor = float(item.calc_waste_factor or 0)
            result *= (1.0 + waste_factor)
            
        elif item.calc_type == CalculationType.AREA:
            # W * H / 1,000,000 (mm2 to m2)
            result = (w * h) / 1000000.0
            waste_factor = float(item.calc_waste_factor or 0)
            result *= (1.0 + waste_factor)
        elif item.calc_type == CalculationType.VOLUME:
            # W * H * L / 1,000,000,000 (mm3 to m3)
            result = (w * h * l) / 1000000000.0
            waste_factor = float(item.calc_waste_factor or 0)
            result *= (1.0 + waste_factor)
        elif item.calc_type == CalculationType.FORMULA:
            result = SpecificationService._evaluate_formula(item.calc_formula, w, h, l, kg, custom_attrs)
            waste_factor = float(item.calc_waste_factor or 0)
            result *= (1.0 + waste_factor)
        elif item.calc_type == CalculationType.FABRIC_CUTTING:
            result = SpecificationService._calc_fabric_cutting(
                item.calc_dim_config or {},
                parent_dimensions,
            )

        return Decimal(str(round(result, 4)))

    @staticmethod
    def resolve_detail_component(
        item: SpecificationItem, 
        parent_dimensions: Dict[str, Any],
        db: Any
    ) -> Optional[Any]:
        """
        Resolves the component (material) for a detail line based on mapping.
        """
        if not item.mapping_attr or not item.material_mapping:
            return item.component

        # Get the value of the mapping attribute from parent characteristics
        custom_attrs = parent_dimensions.get('custom_attributes') or {}
        # Try different sources for the value
        attr_value = custom_attrs.get(item.mapping_attr)
        
        if not attr_value:
            return item.component

        # Find the material ID in mapping
        material_id_str = item.material_mapping.get(str(attr_value))
        if not material_id_str:
            return item.component

        from app.models.product import Product
        try:
            return db.query(Product).filter(Product.id == material_id_str).first()
        except:
            return item.component

    @staticmethod
    def find_matching_variant(
        product: Any,
        target_length: float,
        target_width: Optional[float],
        db: Any
    ) -> Optional[Any]:
        """
        Searches for a variant of the product that matches the calculated dimensions.
        Looks specifically for DIMENSIONS type attributes and compares numeric values.
        """
        if not product or not product.id:
            return None

        from app.models.variant import ProductVariant, ProductVariantValue
        from app.models.attribute import Attribute

        # 1. Get all variants for this product
        variants = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).all()
        
        # 2. Iterate and check attributes
        for v in variants:
            for val in v.values:
                attr = db.query(Attribute).filter(Attribute.id == val.attribute_id).first()
                if attr and attr.type == 'DIMENSIONS':
                    if not val.text_value: continue
                    norm_val = val.text_value.replace('×', 'x').replace('*', 'x').replace(' ', '')
                    parts = norm_val.split('x')
                    if len(parts) < 2: continue
                    
                    try:
                        v_w = float(parts[0])
                        v_h = float(parts[1])
                    except (ValueError, IndexError):
                        continue
                    
                    if target_width:
                        match_1 = (abs(v_w - target_length) < 0.1 and abs(v_h - target_width) < 0.1)
                        match_2 = (abs(v_h - target_length) < 0.1 and abs(v_w - target_width) < 0.1)
                        if match_1 or match_2:
                            return v
                    else:
                        if abs(v_w - target_length) < 0.1 or abs(v_h - target_length) < 0.1:
                            return v
                            
            # Fallback to string search in name
            target_str = f"{int(target_length)}x{int(target_width)}" if target_width else f"{int(target_length)}"
            if target_str in (v.name or ""):
                return v

        return None

    @staticmethod
    def _to_meters(value: float, unit: str) -> float:
        if unit == 'мм': return value / 1000.0
        if unit == 'см': return value / 100.0
        if unit == 'м': return value
        return value / 1000.0 # Standard is mm now

    @staticmethod
    def _calculate_interpolation(item: SpecificationItem, w: float, h: float, l: float, custom_attrs: Dict[str, Any]) -> float:
        dp = item.calc_data_points
        if not dp or not isinstance(dp, dict):
            return float(item.quantity or 0)

        is_meters = item.unit_of_measure == 'м'
        total = 0.0
        has_any_points = False
        
        dim_map = {'h': h, 'w': w, 'l': l}
        config = item.calc_dim_config or {}
        
        for key, physical_val in dim_map.items():
            pts = dp.get(key)
            if not pts or not isinstance(pts, list):
                continue
            
            valid_pts = sorted(
                [p for p in pts if p.get('x') is not None and p.get('qty') is not None],
                key=lambda p: float(p['x'])
            )
            
            if not valid_pts:
                continue
            
            has_any_points = True
            dim_config = config.get(key, {})
            unit = dim_config.get('unit', 'мм')
            char_name = dim_config.get('char_name')
            
            # Resolve dimension value
            dim_val_raw = physical_val
            
            # Global Automation Check
            active_char_name = char_name
            if not active_char_name and item.specification and item.specification.product and item.specification.product.variant_config:
                vcfg = item.specification.product.variant_config
                dim_map_vcfg = {'h': 'height', 'w': 'width', 'l': 'length'}
                g = vcfg.get(dim_map_vcfg.get(key))
                if g and g.get('source') == 'attribute' and g.get('attr_id'):
                    # Search for 'Розмір' or similar common names if not explicitly mapped
                    # In this system, we commonly use names in custom_attrs keys
                    potential_names = ['Розмір', 'Розмір (мм)', 'Size']
                    for p_name in potential_names:
                        if p_name in custom_attrs:
                            active_char_name = p_name
                            break

            if active_char_name and active_char_name in custom_attrs:
                dim_val_raw = float(custom_attrs[active_char_name])
            
            # Normalize dim_val to the unit of interpolation points (config.unit)
            normalized_dim_val = dim_val_raw
            if not active_char_name:
                # Product dimensions are in mm. Convert to config.unit
                if unit == 'см': normalized_dim_val = dim_val_raw / 10.0
                if unit == 'м': normalized_dim_val = dim_val_raw / 1000.0
            else:
                # Characteristics are assumed to be in the unit specified in config.unit
                normalized_dim_val = dim_val_raw

            def interp(p1, p2, x):
                x1, y1 = float(p1['x']), float(p1['qty'])
                x2, y2 = float(p2['x']), float(p2['qty'])
                if x2 == x1:
                    return y1
                slope = (y2 - y1) / (x2 - x1)
                return y1 + slope * (x - x1)

            if len(valid_pts) == 1:
                count_result = float(valid_pts[0]['qty'])
            elif normalized_dim_val <= float(valid_pts[0]['x']):
                count_result = interp(valid_pts[0], valid_pts[1], normalized_dim_val)
            elif normalized_dim_val >= float(valid_pts[-1]['x']):
                count_result = interp(valid_pts[-2], valid_pts[-1], normalized_dim_val)
            else:
                count_result = 0
                for i in range(len(valid_pts) - 1):
                    if normalized_dim_val >= float(valid_pts[i]['x']) and normalized_dim_val <= float(valid_pts[i+1]['x']):
                        count_result = interp(valid_pts[i], valid_pts[i+1], normalized_dim_val)
                        break
            
            dim_final = count_result
            if is_meters:
                # In interpolation mode, we treat count_result as the final absolute value
                # (Same as we fixed in the frontend)
                dim_final = count_result
            
            dim_waste = float(dim_config.get('waste') or 0)
            if dim_waste > 0:
                dim_final *= (1.0 + dim_waste / 100.0)
                
            total += max(0.0, dim_final)

        return total if has_any_points else float(item.quantity or 0)

    @staticmethod
    def _evaluate_formula(formula: str, w: float, h: float, l: float, kg: float, custom_attrs: Dict[str, Any] = None) -> float:
        if not formula:
            return 0.0
        
        custom_attrs = custom_attrs or {}
        
        def replace_custom_attr(match):
            attr_name = match.group(1)
            val = custom_attrs.get(attr_name, 0.0)
            return str(val)
            
        processed_formula = re.sub(r'\{([^}]+)\}', replace_custom_attr, formula)
        
        subs = {
            'W': w,
            'H': h,
            'L': l,
            'KG': kg
        }
        
        for var, val in subs.items():
            processed_formula = re.sub(rf'\b{var}\b', str(val), processed_formula, flags=re.IGNORECASE)
            
        cleaned = re.sub(r'[^0-9.+\-*/%() ]', '', processed_formula)
            
        try:
            return float(eval(cleaned))
        except:
            return 0.0
