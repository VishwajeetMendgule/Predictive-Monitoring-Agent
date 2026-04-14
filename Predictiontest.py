from ReadLogs import readtestlogs,readtrainlogs
from Prediction import lstm_model
from Process_logs import processed_logs
import matplotlib.pyplot as plt

logs,cpu,memory,network = readtestlogs()

test = processed_logs(logs,cpu,memory,network)

logs,cpu,memory,network = readtrainlogs()

train = processed_logs(logs,cpu,memory,network)

predictions = lstm_model(test)

time_steps = 5
# Slice the test data to drop the first 5 rows, aligning it with the predictions
actual_test_data = test.iloc[time_steps:].copy()

# 4. Extract specific features from the 7-column prediction array
# Index mapping: ['cpu'(0), 'memory'(1), 'network'(2), 'DEBUG'(3), 'ERROR'(4), 'INFO'(5), 'WARN'(6)]
actual_test_data['Predicted_CPU'] = predictions[:, 0]
actual_test_data['Predicted_Memory'] = predictions[:, 1]
actual_test_data['Predicted_Errors'] = predictions[:, 4]

# --- PLOTTING ---
plt.figure(figsize=(14, 10))

# Subplot 1: CPU Utilization
plt.subplot(3, 1, 1)
# Use the index or a timestamp column if available for the x-axis
plt.plot(actual_test_data.index, actual_test_data['cpu'], label='Actual CPU', color='blue', linewidth=2)
plt.plot(actual_test_data.index, actual_test_data['Predicted_CPU'], label='Predicted CPU', color='orange', linestyle='dashed', linewidth=2)
plt.title('CPU Utilization: Actual vs Predicted')
plt.ylabel('CPU %')
plt.legend()
plt.grid(True, alpha=0.3)

# Subplot 2: Memory Utilization
plt.subplot(3, 1, 2)
plt.plot(actual_test_data.index, actual_test_data['memory'], label='Actual Memory', color='green', linewidth=2)
plt.plot(actual_test_data.index, actual_test_data['Predicted_Memory'], label='Predicted Memory', color='red', linestyle='dashed', linewidth=2)
plt.title('Memory Utilization: Actual vs Predicted')
plt.ylabel('Memory %')
plt.legend()
plt.grid(True, alpha=0.3)

# Subplot 3: Error Log Counts
plt.subplot(3, 1, 3)
plt.plot(actual_test_data.index, actual_test_data['ERROR'], label='Actual Errors', color='purple', linewidth=2)
plt.plot(actual_test_data.index, actual_test_data['Predicted_Errors'], label='Predicted Errors', color='pink', linestyle='dashed', linewidth=2)
plt.title('Error Counts: Actual vs Predicted')
plt.ylabel('Count')
plt.xlabel('Time (Minutes)')
plt.legend()
plt.grid(True, alpha=0.3)

# Adjust layout to prevent overlapping text
plt.tight_layout()
plt.show()

