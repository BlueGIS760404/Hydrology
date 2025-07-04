import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gumbel_r

# Read annual peak flow data from Excel file
# Assumes Excel file has a column named 'PeakFlow' with discharge values in CMS
def read_peak_flow_data(file_path):
    df = pd.read_excel(file_path)
    return df['PeakFlow'].dropna().values

# Calculate exceedance probabilities and return periods using Gringorten formula
def calculate_probabilities(peak_flows):
    N = len(peak_flows)
    a = 0.44  # Gringorten plotting position parameter
    ranks = np.argsort(np.argsort(peak_flows)[::-1]) + 1  # Rank in descending order
    exceedance_prob = (ranks - a) / (N + 1 - 2 * a)
    non_exceedance_prob = 1 - exceedance_prob
    return_period = 1 / exceedance_prob
    return exceedance_prob, non_exceedance_prob, return_period

# Fit Gumbel distribution and estimate flood magnitude for a given return period
def fit_gumbel_distribution(peak_flows, return_periods):
    # Fit Gumbel distribution parameters
    loc, scale = gumbel_r.fit(peak_flows)
    
    # Calculate theoretical non-exceedance probability and corresponding discharge
    p_theoretical = 1 - 1 / return_periods
    theoretical_flow = gumbel_r.ppf(p_theoretical, loc=loc, scale=scale)
    return theoretical_flow, loc, scale

# Main function for flood frequency analysis
def flood_frequency_analysis(file_path, target_return_period=100):
    # Read data
    peak_flows = read_peak_flow_data(file_path)
    
    # Calculate probabilities and return periods
    exceedance_prob, non_exceedance_prob, return_period = calculate_probabilities(peak_flows)
    
    # Fit Gumbel distribution
    theoretical_flow, loc, scale = fit_gumbel_distribution(peak_flows, return_period)
    
    # Calculate the 100-year flood
    p_100 = 1 - 1 / target_return_period
    flood_100_year = gumbel_r.ppf(p_100, loc=loc, scale=scale)
    
    # Create flood frequency plot
    plt.figure(figsize=(10, 6))
    plt.scatter(return_period, peak_flows[np.argsort(return_period)], label='Observed Data', color='blue')
    plt.plot(np.sort(return_period), theoretical_flow[np.argsort(return_period)], label='Gumbel Fit', color='red')
    plt.xscale('log')
    plt.xlabel('Return Period (years)')
    plt.ylabel('Discharge (CMS)')
    plt.title('Flood Frequency Analysis - Gumbel Distribution')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.savefig('flood_frequency_plot.png')
    plt.close()
    
    # Print results
    print(f"100-year flood estimate: {flood_100_year:.2f} CMS")
    print(f"Gumbel distribution parameters: Location = {loc:.2f}, Scale = {scale:.2f}")
    
    # Save results to a new Excel file
    results_df = pd.DataFrame({
        'PeakFlow': peak_flows,
        'Rank': np.argsort(np.argsort(peak_flows)[::-1]) + 1,
        'Exceedance_Probability': exceedance_prob,
        'Non_Exceedance_Probability': non_exceedance_prob,
        'Return_Period': return_period
    })
    results_df.to_excel('flood_frequency_results.xlsx', index=False)
    print("Results saved to 'flood_frequency_results.xlsx'")

# Example usage
if __name__ == "__main__":
    file_path = "peak_flow_data.xlsx"  # Replace with your Excel file path
    flood_frequency_analysis(file_path)
