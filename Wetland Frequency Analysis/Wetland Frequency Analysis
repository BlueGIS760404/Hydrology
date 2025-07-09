import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gumbel_r, weibull_min, pareto

# Read wetland data from Excel file
# Assumes Excel file has a column (e.g., 'WaterLevel' or 'Storage') with values in meters or cubic meters
def read_wetland_data(file_path, column_name='WaterLevel'):
    df = pd.read_excel(file_path)
    return df[column_name].dropna().values

# Calculate exceedance probabilities and return periods using Gringorten formula
def calculate_wetland_probabilities(data, extreme='high'):
    N = len(data)
    a = 0.44  # Gringorten plotting position parameter
    if extreme == 'high':
        ranks = np.argsort(np.argsort(data)[::-1]) + 1  # Rank in descending order for high extremes
    else:  # For low extremes (e.g., drought)
        ranks = np.argsort(np.argsort(data)) + 1  # Rank in ascending order
    exceedance_prob = (ranks - a) / (N + 1 - 2 * a)
    non_exceedance_prob = 1 - exceedance_prob
    return_period = 1 / exceedance_prob
    return exceedance_prob, non_exceedance_prob, return_period

# Fit distribution (Gumbel or Weibull) and estimate values for given return periods
def fit_distribution(data, return_periods, distribution='gumbel', extreme='high'):
    if distribution == 'gumbel':
        loc, scale = gumbel_r.fit(data)
        p_theoretical = 1 - 1 / return_periods if extreme == 'high' else 1 / return_periods
        theoretical_values = gumbel_r.ppf(p_theoretical, loc=loc, scale=scale)
    elif distribution == 'weibull':
        shape, loc, scale = weibull_min.fit(data)
        p_theoretical = 1 - 1 / return_periods if extreme == 'low' else 1 / return_periods
        theoretical_values = weibull_min.ppf(p_theoretical, shape, loc=loc, scale=scale)
    else:
        raise ValueError("Distribution must be 'gumbel' or 'weibull'")
    return theoretical_values, loc, scale

# Peak-over-threshold (POT) analysis for extreme events
def peak_over_threshold(data, threshold, extreme='high'):
    if extreme == 'high':
        exceedances = data[data > threshold] - threshold
    else:
        exceedances = threshold - data[data < threshold]
    if len(exceedances) == 0:
        raise ValueError("No data points exceed the threshold")
    shape, loc, scale = pareto.fit(exceedances)
    return exceedances, shape, loc, scale

# Main function for wetland frequency analysis
def wetland_frequency_analysis(file_path, target_return_period=100, column_name='WaterLevel', 
                              extreme='high', distribution='gumbel', threshold=None):
    # Read data
    data = read_wetland_data(file_path, column_name)
    
    # Perform POT analysis if threshold is provided
    if threshold is not None:
        exceedances, shape, loc, scale = peak_over_threshold(data, threshold, extreme)
        print(f"POT Analysis: {len(exceedances)} exceedances detected above threshold {threshold}")
        print(f"Pareto distribution parameters: Shape = {shape:.2f}, Location = {loc:.2f}, Scale = {scale:.2f}")
        
        # Save POT results
        results_df = pd.DataFrame({
            'Exceedances': exceedances + threshold if extreme == 'high' else threshold - exceedances,
            'Threshold': [threshold] * len(exceedances)
        })
        results_df.to_excel(f'wetland_pot_results_{extreme}.xlsx', index=False)
        print(f"POT results saved to 'wetland_pot_results_{extreme}.xlsx'")
        return  # Exit after POT analysis

    # Calculate probabilities
    exceedance_prob, non_exceedance_prob, return_period = calculate_wetland_probabilities(data, extreme)
    
    # Fit distribution
    theoretical_values, loc, scale = fit_distribution(data, return_period, distribution, extreme)
    
    # Estimate target return period event
    p_target = 1 - 1 / target_return_period if extreme == 'high' else 1 / target_return_period
    if distribution == 'gumbel':
        target_event = gumbel_r.ppf(p_target, loc=loc, scale=scale)
    else:
        shape, loc, scale = weibull_min.fit(data)
        target_event = weibull_min.ppf(p_target, shape, loc=loc, scale=scale)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.scatter(return_period, data[np.argsort(return_period)], label='Observed Data', color='blue')
    plt.plot(np.sort(return_period), theoretical_values[np.argsort(return_period)], 
             label=f'{distribution.capitalize()} Fit', color='red')
    plt.xscale('log')
    plt.xlabel('Return Period (years)')
    plt.ylabel('Water Level (m)' if column_name == 'WaterLevel' else 'Storage (m³)')
    plt.title(f'Wetland Frequency Analysis - {extreme.capitalize()} Extremes')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.savefig(f'wetland_frequency_plot_{extreme}.png')
    plt.close()
    
    # Print results
    print(f"{target_return_period}-year {extreme} event estimate: {target_event:.2f} {'m' if column_name == 'WaterLevel' else 'm³'}")
    print(f"{distribution.capitalize()} distribution parameters: Location = {loc:.2f}, Scale = {scale:.2f}")
    
    # Save results
    results_df = pd.DataFrame({
        column_name: data,
        'Rank': np.argsort(np.argsort(data)[::-1]) + 1 if extreme == 'high' else np.argsort(np.argsort(data)) + 1,
        'Exceedance_Probability': exceedance_prob,
        'Non_Exceedance_Probability': non_exceedance_prob,
        'Return_Period': return_period
    })
    results_df.to_excel(f'wetland_frequency_results_{extreme}.xlsx', index=False)
    print(f"Results saved to 'wetland_frequency_results_{extreme}.xlsx'")

# Example usage
if __name__ == "__main__":
    file_path = "wetland_data.xlsx"  # Replace with your Excel file path
    # Analyze high water levels (flooding) with Gumbel distribution
    wetland_frequency_analysis(file_path, target_return_period=100, column_name='WaterLevel', 
                              extreme='high', distribution='gumbel')
    # Analyze low water levels (drought) with Weibull distribution
    wetland_frequency_analysis(file_path, target_return_period=100, column_name='WaterLevel', 
                              extreme='low', distribution='weibull')
    # Optional: Perform POT analysis for extreme high water levels
    wetland_frequency_analysis(file_path, column_name='WaterLevel', extreme='high', threshold=2.0)
