import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns


# Load the data into a Pandas dataframe
df = pd.read_csv('wc_dataset_processed_noise_removed.csv')
data = df.drop('event_time', axis=1)
print(data.head(10))

# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(data)

# Apply PCA
pca = PCA(n_components=3)
pca.fit(X_scaled)
scores = pca.transform(X_scaled)
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

print(loadings)
# Plot the scores and arrows
# fig, ax = plt.subplots(figsize=(10,10))
# ax.scatter(scores[:, 1], scores[:, 2])
# for i, (x, y) in enumerate(loadings[:, :2]):
#     ax.arrow(0, 0, x*10, y*10, head_width=0.1, head_length=0.1, linewidth=2, fc='r', ec='r')
#     ax.text(x* 11, y * 11, data.columns[i], color='black', ha='center', va='center', fontsize=12)
# ax.set_xlabel("PC2 ({:.2f}%)".format(100 * pca.explained_variance_ratio_[1]))
# ax.set_ylabel("PC3 ({:.2f}%)".format(100 * pca.explained_variance_ratio_[2]))
# plt.grid()
# plt.show()


fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111, projection='3d')
# ax = fig.add_subplot(122, projection='3d')
ax.scatter(loadings[:,0]*15, loadings[:,1]*15, loadings[:,2]*15, c=['r', 'g', 'b'])
# ax.scatter(scores[:,0], scores[:,1], scores[:,2])
for i, (x, y, z) in enumerate(loadings):
    ax.plot([0, x*15], [0, y*15], [0, z*15], color='red', linewidth=2)
    ax.text(x* 16, y * 16, z * 16, data.columns[i], color='black', ha='center', va='center', fontsize=12)
ax.set_xlabel("PC1 ({:.2f}%)".format(100 * pca.explained_variance_ratio_[0]))
ax.set_ylabel("PC2 ({:.2f}%)".format(100 * pca.explained_variance_ratio_[1]))
ax.set_zlabel("PC3 ({:.2f}%)".format(100 * pca.explained_variance_ratio_[2]))
ax.set_title('Loading plot in 3D')
plt.show()


# # Perform PCA
# pca = PCA(n_components=3)
# pca.fit(X_std)
# # Tính toán các điểm dữ liệu mới trong không gian 3 chiều
# X_pca = pca.transform(X_std) #scaled


# # # Get the transformed data using the first three principal components
# # transformed_data = pca.transform(X_std)[:, :3]

# # # Compute the correlations between the original data and each principal component
# # correlations = np.corrcoef(X_std.T, transformed_data.T)[:3, 3:]

# # # Plot the correlations as a heatmap
# # fig, ax = plt.subplots(figsize=(6, 6))
# # sns.heatmap(correlations, annot=True, cmap='coolwarm', ax=ax)
# # ax.set_xticklabels(['PC1', 'PC2', 'PC3'])
# # ax.set_yticklabels(['event_count', 'sum_bytes', 'num_match_event'], rotation=0)
# # ax.set_title('Correlations between original data and principal components')
# # plt.show()


# # Vẽ biểu đồ PCA 3D
# fig = plt.figure(figsize=(8,8))
# ax = fig.add_subplot(111, projection='3d')
# # ax = fig.add_subplot(111)
# ax.scatter(pcs[:,0], pcs[:,1], pcs[:,2])
# # ax.scatter(pcs[:,0], pcs[:,1])
# ax.set_xlabel('PCA 1')
# ax.set_ylabel('PCA 2')
# ax.set_zlabel('PCA 3')
# plt.show()

