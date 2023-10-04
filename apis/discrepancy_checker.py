import numpy as np

# ANSI escape codes for text color
RED = "\033[91m"
GREEN = "\033[92m"
ENDC = "\033[0m"

class DiscrepancyChecker:
    def __init__(self):
        self.rules = {
            "Soil Gradation (mm)": self.check_soil_gradation_statistical,
            "Atterberg Limits (%)": self.check_atterberg_limits_statistical,
            "Natural Moisture Content (%)": self.check_moisture_content_statistical,
            "Proctor Density (%)": self.check_proctor_density_cent_statistical,
            "Proctor Density (g/cm³)": self.check_proctor_density_statistical,
            "CBR (%)": self.check_cbr_statistical,
            "Swelling Index (%)": self.check_swellingindex_statistical,
            "Moisture Content at the time of Compaction (%)": self.check_moisture_comp_statistical,
            "Thickness (inches)": self.check_thickness_statistical,
            "Field Density (%)": self.check_field_density_statistical,
            "Horizontal alignment (%)": self.check_horizontal_alignment_cent_statistical,
            "Horizontal alignment (m)": self.check_horizontal_alignment_statistical,
        }

    def check_soil_gradation_statistical(self, gradation_values):
        # Perform statistical analysis for Soil Gradation
        median_gradation = np.median(gradation_values)  # Calculate median
        # Define your statistical threshold based on project requirements
        median_gradation_threshold = 1.6  # Adjust as needed
        # Check if the median is within acceptable limits
        if (0.425 <= median_gradation <= 2.0):
            return "No discrepancy"
        else:
            return "Discrepancy: Soil Gradation statistical analysis indicates an issue."

    def check_atterberg_limits_statistical(self, ll_values, pl_values, pi_values):
        # Statistical analysis for Atterberg Limits
        median_ll = np.median(ll_values)  # Calculate median
        median_pl = np.median(pl_values)  # Calculate median
        median_pi = np.median(pi_values)  # Calculate median

        # Define thresholds for Atterberg Limits
        ll_threshold = 35  # Liquid Limit threshold
        pl_threshold = 25  # Plastic Limit threshold
        pi_threshold = 10  # Plasticity Index threshold

        # Check if the median values are within acceptable limits
        discrepancies = []
        if median_ll <= ll_threshold:
            discrepancies.append(f"Discrepancy: Liquid Limit ({median_ll:.2f}%) exceeds the specified limit (< {ll_threshold}%).")
        if median_pl <= pl_threshold:
            discrepancies.append(f"Discrepancy: Plastic Limit ({median_pl:.2f}%) exceeds the specified limit (< {pl_threshold}%).")
        if median_pi <= pi_threshold:
            discrepancies.append(f"Discrepancy: Plasticity Index ({median_pi:.2f}%) exceeds the specified limit (< {pi_threshold}%).")

        if discrepancies:
            return "\n".join(discrepancies)
        else:
            return "No discrepancy"

    def check_moisture_content_statistical(self, subgrade_values, base_subbase_values):
        # Statistical analysis for Moisture Content
        median_subgrade = np.median(subgrade_values)  # Calculate median
        median_base_subbase = np.median(base_subbase_values)  # Calculate median

        # Define thresholds for Moisture Content
        subgrade_threshold = (5, 15)  # Subgrade material range
        base_subbase_threshold = (1, 3)  # Base and Sub-base Materials range

        # Check if the median values are within acceptable limits
        if (subgrade_threshold[0] <= median_subgrade <= subgrade_threshold[1]) and \
           (base_subbase_threshold[0] <= median_base_subbase <= base_subbase_threshold[1]):
            return "No discrepancy"
        else:
            return "Discrepancy: Moisture Content is out of the specified range."


    def check_proctor_density_cent_statistical(self, omc_values):
        # Statistical analysis for Proctor Density
        median_omc = np.median(omc_values)  # Calculate median

        # Define thresholds for Proctor Density
        omc_threshold = (8, 16)  # Optimum Moisture Content range

        # Check if the median values are within acceptable limits
        if (omc_threshold[0] <= median_omc <= omc_threshold[1]):
            return "No discrepancy"
        else:
            return "Discrepancy: Proctor Density is out of the specified range."
        
    def check_proctor_density_statistical(self, mdd_values):
        # Statistical analysis for Proctor Density
        median_mdd = np.median(mdd_values)  # Calculate median

        # Define thresholds for Proctor Density
        mdd_threshold = (1.6, 2.2)  # Maximum Dry Density range

        # Check if the median values are within acceptable limits
        if (mdd_threshold[0] <= median_mdd <= mdd_threshold[1]):
            return "No discrepancy"
        else:
            return "Discrepancy: Proctor Density is out of the specified range."

    def check_cbr_statistical(self, subgrade_cbr_values, base_course_cbr_values, subbase_cbr_values):
        # Statistical analysis for CBR
        median_subgrade_cbr = np.median(subgrade_cbr_values)  # Calculate median
        median_base_course_cbr = np.median(base_course_cbr_values)  # Calculate median
        median_subbase_cbr = np.median(subbase_cbr_values)  # Calculate median

        # Define thresholds for CBR
        subgrade_cbr_threshold = (2, 10)  # Subgrade range
        base_course_cbr_threshold = (20, 80)  # Base Course range
        subbase_cbr_threshold = (10, 40)  # Sub-base range

        # Check if the median values are within acceptable limits
        if (subgrade_cbr_threshold[0] <= median_subgrade_cbr <= subgrade_cbr_threshold[1]) and \
           (base_course_cbr_threshold[0] <= median_base_course_cbr <= base_course_cbr_threshold[1]) and \
           (subbase_cbr_threshold[0] <= median_subbase_cbr <= subbase_cbr_threshold[1]):
            return "No discrepancy"
        else:
            return "Discrepancy: CBR is out of the specified range."

    def check_swellingindex_statistical(self, swellingindex_values):
        # Statistical analysis for Swelling Index
        median_swellingindex = np.median(swellingindex_values)  # Calculate median

        # Define threshold for Swelling Index
        swellingindex_threshold = 20

        # Check if the median value is within acceptable limits
        if median_swellingindex < swellingindex_threshold:
            return "No discrepancy"
        else:
            return "Discrepancy: Swelling Index exceeds the specified limit."

    def check_moisture_comp_statistical( self, moisture_comp_values):
        # Statistical analysis for moisture_comp_values
        median_moisture_comp = np.median(moisture_comp_values)  # Calculate median

        # Define threshold for Moisture Content at the time of Compaction
        moisture_comp_threshold = (2, 4)

        # Check if the median value is within acceptable limits
        if (moisture_comp_threshold[0] <=  median_moisture_comp <=  moisture_comp_threshold[1]):
            return "No discrepancy"
        else:
            return "Discrepancy: Moisture Content at the time of Compaction exceeds the specified limit."

    def check_thickness_statistical(self, thickness_values):
        # Statistical analysis for Thickness
        median_thickness = np.median(thickness_values)  # Calculate median

        # Define threshold for Thickness
        thickness_threshold = (4, 12)

        # Check if the median value is within acceptable limits
        if (thickness_threshold[0] <= median_thickness <= thickness_threshold[1]):
            return "No discrepancy"
        else:
            return "Discrepancy: Thickness is out of the specified range."

    def check_field_density_statistical(self, field_density_values):
        # Statistical analysis for Field Density
        median_field_density = np.median(field_density_values)  # Calculate median

        # Define threshold for Field Density
        field_density_threshold = (95, 100)

        # Check if the median value is within acceptable limits
        if (field_density_threshold[0] <= median_field_density <= field_density_threshold[1]):
            return "No discrepancy"
        else:
            return "Discrepancy: Field Density is out of the specified range."

    def check_horizontal_alignment_cent_statistical(self, superelevation_values, grade_values):
        # Perform statistical analysis for Horizontal Alignment
        median_superelevation = np.median(superelevation_values)  # Calculate median

        median_grade = np.median(grade_values)  # Calculate median

        # Define statistical thresholds based on project requirements
        median_radius_threshold = 250.0  # Adjust as needed
        median_superelevation_threshold = 7.0  # Adjust as needed
        median_transition_length_threshold = 150.0  # Adjust as needed
        median_curve_length_threshold = 200.0  # Adjust as needed
        median_grade_threshold = 6.0  # Adjust as needed

        # Check if the medians are within acceptable limits
        if (4 <= median_superelevation <= 10) and (4 <= median_grade <= 8):
            return "No discrepancy"
        else:
            return "Discrepancy: Horizontal Alignment statistical analysis indicates an issue."
        
    def check_horizontal_alignment_statistical(self, radius_values,
                                                transition_length_values, curve_length_values):
        # Perform statistical analysis for Horizontal Alignment
        median_radius = np.median(radius_values)  # Calculate median
        median_transition_length = np.median(transition_length_values)  # Calculate median
        median_curve_length = np.median(curve_length_values)  # Calculate median

        # Define statistical thresholds based on project requirements
        median_radius_threshold = 250.0  # Adjust as needed
        median_superelevation_threshold = 7.0  # Adjust as needed
        median_transition_length_threshold = 150.0  # Adjust as needed
        median_curve_length_threshold = 200.0  # Adjust as needed
        median_grade_threshold = 6.0  # Adjust as needed

        # Check if the medians are within acceptable limits
        if (120 <= median_radius <= 300) and (20 <= median_transition_length <= 200) and (50 <= median_curve_length <= 300):
            return "No discrepancy"
        else:
            return "Discrepancy: Horizontal Alignment statistical analysis indicates an issue."


    def check_parameters(self, test_report_name, parameters):
        discrepancies = {}
        for parameter, value in parameters.items():
            if parameter in self.rules:
                result = self.rules[parameter](*value)
                if result != "No discrepancy":
                    discrepancies.setdefault(test_report_name, {})[parameter] = {
                        "discrepancy": result,
                        "suggestion": self.get_suggestion(parameter, value)
                    }
                else:
                    discrepancies.setdefault(test_report_name, {})[parameter] = {
                        "discrepancy": "No discrepancy",
                        "suggestion": ""
                    }
        return discrepancies

    def get_suggestion(self, parameter, value):
        if parameter == "Soil Gradation (mm)":
            return "Suggestion: Ensure soil gradation falls within the range of 0.425 mm - 2 mm."
        elif parameter == "Atterberg Limits (%)":
            return "Suggestion: Check and adjust LL, PL, and PI values within acceptable limits."
        elif parameter == "Natural Moisture Content (%)":
            return "Suggestion: Verify and adjust moisture content for subgrade and base/sub-base materials."
        elif parameter == "Proctor Density (g/cm³ & %)":
            return "Suggestion: Ensure the Maximum Dry Density (MDD) is between 1.6 g/cm³ and 2.2 g/cm³."
        elif parameter == "Proctor Density (%)":
            return "Suggestion: Ensure the Optimum Moisture Content (OMC) is between 8% to 16%"
        elif parameter == "CBR (%)":
            return "Suggestion: Check and adjust CBR values for subgrade, base course, and sub-base."
        elif parameter == "Swelling Index (%)":
            return "Suggestion: Reduce swelling index to less than 20%."
        elif parameter == "Moisture Content at the time of Compaction (%)":
            return "Suggestion: Adjust the Moisture Content at the time of Compaction to be within the range of 2% to 4%"
        elif parameter == "Thickness (inches)":
            return "Suggestion: Adjust the thickness to be within the range of 4-12 inches."
        elif parameter == "Field Density (%)":
            return "Suggestion: Ensure field density is between 95% and 100%."
        elif parameter == "Horizontal alignment (%)":
            return "Suggestion: Review and adjust horizontal alignment parameters according to this ranges: Superelevation (Banking) as 4-10% and Grade (Slope) as 4-8%"
        elif parameter == "Horizontal alignment (m)":
            return "Suggestion: Review and adjust horizontal alignment parameters according to this ranges: Radius of Curvature (R) as 120-300m, Transition Curve Length (L) as 20-200m and Horizontal Curve Length (Lc) as 50-300m"
        

    def print_discrepancies(self, discrepancies):
        for test_name, params in discrepancies.items():
            print(f"Test Report: {test_name}")
            for param, values in params.items():
                print(f"Parameter: {param}")
                if values["discrepancy"] == "No discrepancy":
                    print(f"{GREEN}Discrepancy: No{ENDC}")
                else:
                    print(f"{RED}Discrepancy: Yes\n  - {values['discrepancy']}{ENDC}")
                    print(f"Suggestion: {values['suggestion']}")
            print()