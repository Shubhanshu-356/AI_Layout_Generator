import random
from shapely.geometry import box

# --- CONFIGURATION & CONSTANTS ---
SITE_WIDTH = 200
SITE_HEIGHT = 140
BOUNDARY_BUFFER = 10  # Rule 3: 10m from site edge
BUILDING_GAP = 15     # Rule 2: 15m between buildings
PLAZA_SIZE = 40       # Rule 5: 40x40m central plaza
MIX_RULE_DIST = 60    # Rule 4: Tower B within 60m of Tower A

# Building Dimensions
TOWER_A_DIMS = (30, 20) 
DEFAULT_TOWER_B_WIDTH = 40 

class Building:
    def __init__(self, x, y, width, height, b_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = b_type
        # Create a geometric box for collision calculations
        self.poly = box(x, y, x + width, y + height)

    def distance_to(self, other_building):
        return self.poly.distance(other_building.poly)

class LayoutGenerator:
    def __init__(self, num_a, num_b, tower_b_width):
        self.buildings = []
        # Define the Plaza (Rule 5) - Center of the site
        self.plaza = box(
            (SITE_WIDTH / 2) - (PLAZA_SIZE / 2),
            (SITE_HEIGHT / 2) - (PLAZA_SIZE / 2),
            (SITE_WIDTH / 2) + (PLAZA_SIZE / 2),
            (SITE_HEIGHT / 2) + (PLAZA_SIZE / 2)
        )
        self.target_a = num_a
        self.target_b = num_b
        self.tower_b_dims = (tower_b_width, 20)

    def is_valid_position(self, new_b):
        # Rule 1 & 3: Check Boundary (must be inside site AND 10m from edge)
        safe_x_min = BOUNDARY_BUFFER
        safe_y_min = BOUNDARY_BUFFER
        safe_x_max = SITE_WIDTH - BOUNDARY_BUFFER
        safe_y_max = SITE_HEIGHT - BOUNDARY_BUFFER

        if (new_b.x < safe_x_min or 
            new_b.y < safe_y_min or 
            (new_b.x + new_b.width) > safe_x_max or 
            (new_b.y + new_b.height) > safe_y_max):
            return False

        # Rule 5: Check Plaza Overlap (No footprint inside plaza)
        if new_b.poly.intersects(self.plaza):
            return False

        # Rule 2: Check Distance to other buildings (15m gap)
        for b in self.buildings:
            if new_b.distance_to(b) < BUILDING_GAP:
                return False
        
        return True

    def generate(self, max_attempts=1500):
        self.buildings = []
        # Create a list of buildings to place
        to_place = ['A'] * self.target_a + ['B'] * self.target_b
        random.shuffle(to_place) # Shuffle to randomize placement order

        for b_type in to_place:
            w, h = TOWER_A_DIMS if b_type == 'A' else self.tower_b_dims
            
            # Try to place this specific building
            for _ in range(max_attempts):
                # Pick a random spot
                rx = random.uniform(BOUNDARY_BUFFER, SITE_WIDTH - BOUNDARY_BUFFER - w)
                ry = random.uniform(BOUNDARY_BUFFER, SITE_HEIGHT - BOUNDARY_BUFFER - h)
                
                # Randomly rotate 90 degrees?
                if random.choice([True, False]):
                    cur_w, cur_h = h, w # Swap width/height
                else:
                    cur_w, cur_h = w, h
                
                # Check if rotation pushes it out of bounds
                if rx + cur_w > SITE_WIDTH - BOUNDARY_BUFFER or ry + cur_h > SITE_HEIGHT - BOUNDARY_BUFFER:
                    continue

                candidate = Building(rx, ry, cur_w, cur_h, b_type)
                
                if self.is_valid_position(candidate):
                    self.buildings.append(candidate)
                    break 
    
    def check_mix_rule(self):
        """Rule 4: Every Tower A must have a Tower B within 60m."""
        towers_a = [b for b in self.buildings if b.type == 'A']
        towers_b = [b for b in self.buildings if b.type == 'B']
        
        if not towers_a: return True, 0
        if not towers_b: return False, len(towers_a) 

        violations = 0
        for a in towers_a:
            has_neighbor = False
            for b in towers_b:
                if a.distance_to(b) <= MIX_RULE_DIST:
                    has_neighbor = True
                    break
            if not has_neighbor:
                violations += 1
        return violations == 0, violations

    def get_stats(self):
        count_a = len([b for b in self.buildings if b.type == 'A'])
        count_b = len([b for b in self.buildings if b.type == 'B'])
        area = sum([b.width * b.height for b in self.buildings])
        mix_ok, violations = self.check_mix_rule()
        
        return {
            "Count A": count_a,
            "Count B": count_b,
            "Total Area": area,
            "Mix Rule Met": mix_ok,
            "Mix Violations": violations
        }