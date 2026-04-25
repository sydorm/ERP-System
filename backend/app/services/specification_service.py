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
        parent_dimensions should contain: 'width_cm', 'height_cm', 'length_cm', 'weight_kg', 'custom_attributes'
        """
        if not item.is_calculated or item.calc_type == CalculationType.FIXED:
            return Decimal(str(item.quantity or 0))

        w = float(parent_dimensions.get('width_cm') or 0)
        h = float(parent_dimensions.get('height_cm') or 0)
        l = float(parent_dimensions.get('length_cm') or 0)
        kg = float(parent_dimensions.get('weight_kg') or 0)
        custom_attrs = parent_dimensions.get('custom_attributes') or {}

        result = 0.0

        if item.calc_type == CalculationType.INTERPOLATION:
            result = SpecificationService._calculate_interpolation(item, w, h, l)
        elif item.calc_type == CalculationType.AREA:
            # W * H / 10000 (cm2 to m2)
            result = (w * h) / 10000.0
        elif item.calc_type == CalculationType.VOLUME:
            # W * H * L / 1000000 (cm3 to m3)
            result = (w * h * l) / 1000000.0
        elif item.calc_type == CalculationType.FORMULA:
            result = SpecificationService._evaluate_formula(item.calc_formula, w, h, l, kg, custom_attrs)
        
        # Apply waste factor
        waste_factor = float(item.calc_waste_factor or 0)
        result *= (1.0 + waste_factor)

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
        Expects variant characteristics to contain the size (e.g. "600x320").
        """
        if not product or not product.id:
            return None

        from app.models.variant import ProductVariant
        from sqlalchemy import or_

        # Get all variants of this material
        variants = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).all()
        
        # Simple heuristic: look for variants where characteristic name or value contains the size
        # Most common format: "600x320"
        target_str_1 = f"{int(target_length)}x{int(target_width)}" if target_width else f"{int(target_length)}x"
        target_str_2 = f"{int(target_width)}x{int(target_length)}" if target_width else f"x{int(target_length)}"
        
        for v in variants:
            v_name = v.name or ""
            if target_str_1 in v_name or target_str_2 in v_name:
                return v
            
            # Check values
            for val in v.values:
                val_str = str(val.value or "")
                if target_str_1 in val_str or target_str_2 in val_str:
                    return v
                    
        return None

    @staticmethod
    def _calculate_interpolation(item: SpecificationItem, w: float, h: float, l: float) -> float:
        dp = item.calc_data_points
        if not dp or not isinstance(dp, dict):
            return float(item.quantity or 0)

        total = 0.0
        has_any_points = False
        
        dim_map = {'w': w, 'h': h, 'l': l}
        
        for key, val in dim_map.items():
            pts = dp.get(key)
            if not pts or not isinstance(pts, list):
                continue
            
            # Filter and sort points by x
            valid_pts = sorted(
                [p for p in pts if p.get('x') is not None and p.get('qty') is not None],
                key=lambda p: float(p['x'])
            )
            
            if not valid_pts:
                continue
            
            has_any_points = True
            
            def interp(p1, p2, x):
                x1, y1 = float(p1['x']), float(p1['qty'])
                x2, y2 = float(p2['x']), float(p2['qty'])
                if x2 == x1:
                    return y1
                slope = (y2 - y1) / (x2 - x1)
                return y1 + slope * (x - x1)

            if len(valid_pts) == 1:
                dim_result = float(valid_pts[0]['qty'])
            elif val <= float(valid_pts[0]['x']):
                dim_result = interp(valid_pts[0], valid_pts[1], val)
            elif val >= float(valid_pts[-1]['x']):
                dim_result = interp(valid_pts[-2], valid_pts[-1], val)
            else:
                dim_result = 0
                for i in range(len(valid_pts) - 1):
                    if val >= float(valid_pts[i]['x']) and val <= float(valid_pts[i+1]['x']):
                        dim_result = interp(valid_pts[i], valid_pts[i+1], val)
                        break
            
            total += max(0.0, dim_result)

        return total if has_any_points else float(item.quantity or 0)

    @staticmethod
    def _evaluate_formula(formula: str, w: float, h: float, l: float, kg: float, custom_attrs: Dict[str, float] = None) -> float:
        if not formula:
            return 0.0
        
        custom_attrs = custom_attrs or {}
        
        # 1. Replace custom attributes like {AttributeName} with their values
        # We find matches and attempt to lookup the key in custom_attrs.
        # If not found, defaults to 0.0
        def replace_custom_attr(match):
            attr_name = match.group(1)
            # Find attribute case-insensitively, or exact match depending on input
            # By default, match exactly
            return str(custom_attrs.get(attr_name, 0.0))
            
        safe_formula = re.sub(r'\{([^}]+)\}', replace_custom_attr, formula)
        
        # 2. Simple/Safe evaluation for basic math formulas
        safe_formula = safe_formula.upper()
        subs = {
            'W': w,
            'H': h,
            'L': l,
            'KG': kg
        }
        
        # Replace base variables
        for var, val in subs.items():
            safe_formula = re.sub(rf'\b{var}\b', str(val), safe_formula)
            
        # Limit characters to numbers, operators, and parentheses
        if not re.match(r'^[0-9.+\-*/%() ]*$', safe_formula):
            return 0.0
            
        try:
            return float(eval(safe_formula))
        except:
            return 0.0
