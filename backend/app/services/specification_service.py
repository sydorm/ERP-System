from typing import List, Dict, Any, Optional
import re
from decimal import Decimal
from app.models.specification import SpecificationItem, CalculationType, CalculationDimension

class SpecificationService:
    @staticmethod
    def calculate_item_quantity(
        item: SpecificationItem, 
        parent_dimensions: Dict[str, float]
    ) -> Decimal:
        """
        Calculates the quantity of a component based on smart rules.
        parent_dimensions should contain: 'width_cm', 'height_cm', 'length_cm', 'weight_kg'
        """
        if not item.is_calculated or item.calc_type == CalculationType.FIXED:
            return Decimal(str(item.quantity or 0))

        w = float(parent_dimensions.get('width_cm') or 0)
        h = float(parent_dimensions.get('height_cm') or 0)
        l = float(parent_dimensions.get('length_cm') or 0)
        kg = float(parent_dimensions.get('weight_kg') or 0)

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
            result = SpecificationService._evaluate_formula(item.calc_formula, w, h, l, kg)
        
        # Apply waste factor
        waste_factor = float(item.calc_waste_factor or 0)
        result *= (1.0 + waste_factor)

        return Decimal(str(round(result, 4)))

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
    def _evaluate_formula(formula: str, w: float, h: float, l: float, kg: float) -> float:
        if not formula:
            return 0.0
        
        # Simple/Safe evaluation for basic math formulas
        # We replace variables with their values
        safe_formula = formula.upper()
        # Replace variables (order matters to avoid partial replacement)
        subs = {
            'W': w,
            'H': h,
            'L': l,
            'KG': kg
        }
        
        # Use regex to find standalone variables
        for var, val in subs.items():
            safe_formula = re.sub(rf'\b{var}\b', str(val), safe_formula)
            
        # Limit characters to numbers, operators, and parentheses
        if not re.match(r'^[0-9.+\-*/%() ]*$', safe_formula):
            return 0.0
            
        try:
            # Note: eval is generally unsafe, but here we strictly filtered characters 
            # and it's a controlled environment. 
            # In a true prod system, use a proper math parser like 'numexpr' or 'simpleeval'.
            return float(eval(safe_formula))
        except:
            return 0.0
