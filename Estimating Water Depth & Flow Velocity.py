import numpy as np
import pandas as pd

def calculate_velocity(depth, width, slope, manning_n):
    """
    Calculate water velocity using Manning's equation for a rectangular channel.
    
    Parameters:
    - depth (float): Water depth (m)
    - width (float): Channel width (m)
    - slope (float): Channel slope (m/m)
    - manning_n (float): Manning's roughness coefficient
    
    Returns:
    - velocity (float): Water velocity (m/s)
    """
    try:
        # Calculate cross-sectional area (A = width * depth)
        area = width * depth
        
        # Calculate wetted perimeter (P = width + 2 * depth)
        wetted_perimeter = width + 2 * depth
        
        # Calculate hydraulic radius (R = A / P)
        hydraulic_radius = area / wetted_perimeter
        
        # Manning's equation: V = (1/n) * R^(2/3) * S^(1/2)
        velocity = (1 / manning_n) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
        
        return velocity
    except ZeroDivisionError:
        return np.nan
    except ValueError:
        return np.nan

def main():
    """
    Main function to calculate water depth and velocity for multiple depth inputs.
    Outputs results to console and saves to a CSV file.
    """
    # User-defined channel parameters
    width = float(input("Enter channel width (m, e.g., 10): ") or 10.0)
    slope = float(input("Enter channel slope (m/m, e.g., 0.001): ") or 0.001)
    manning_n = float(input("Enter Manning's roughness coefficient (e.g., 0.035): ") or 0.035)
    
    # Define a range of water depths to evaluate (e.g., 0.5m to 3.0m)
    depths = np.arange(0.5, 3.1, 0.5)  # [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    
    # Calculate velocity for each depth
    results = []
    for depth in depths:
        velocity = calculate_velocity(depth, width, slope, manning_n)
        results.append({
            "Depth (m)": round(depth, 2),
            "Velocity (m/s)": round(velocity, 3) if not np.isnan(velocity) else np.nan
        })
    
    # Create DataFrame for results
    df = pd.DataFrame(results)
    
    # Display results
    print("\nWater Depth and Velocity Calculations:")
    print(df.to_string(index=False))
    
    # Save results to CSV
    output_file = "water_depth_velocity_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"Error: Invalid input. Please enter numeric values. {e}")
