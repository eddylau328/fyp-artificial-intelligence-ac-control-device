import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from psychrochart import PsychroChart
from sklearn.decomposition import PCA
from sklearn import preprocessing
from enum import Enum
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score
import random


def num_of_paths():
    i = 1
    found = False
    while (not found):
        filepath = 'env_training_data/env_data_'+str(i)
        try:
            with open(filepath +'.json', 'r') as file:
                i += 1
                # Do something with the file
        except IOError:
            found = True
    return i-1

def get_data(path, dataname):
    with open(path, 'r') as file:
        json_file = json.load(file)
    return json_file[dataname]


class Feedback(Enum):
    very_hot = 0
    hot = 1
    a_bit_hot = 2
    comfy = 3
    a_bit_cold = 4
    cold = 5
    very_cold = 6


parameters = {
    'input_shape':17,
    'data_name':['temp','hum','outdoor_temp','outdoor_hum','body','set_temp','set_fanspeed','feedback'],
    'x':['temp','hum','body','outdoor_temp','outdoor_hum','set_fanspeed'],
    'y':['feedback'],
    'normalize':['temp','hum','outdoor_temp','outdoor_hum','body','set_fanspeed'],
    'output_shape': len(Feedback),
    'feedback_amplifier': 4,
    'replace_acceptable': True,
    'model_name': "Supervised Learning"
}


data_name = parameters['data_name']
feedback_amplifier = parameters['feedback_amplifier']
replace_acceptable = parameters['replace_acceptable']
normalize_data_name = parameters['normalize']
normalize_max_min = []
x_field = parameters['x']
y_field = parameters['y']



def get_x_y():
    data = extract_data()
    data = amplify_feedback(data)
    data = process_data(data)
    x = []
    for dict_obj in data:
        x_data = []
        for key in x_field:
            x_data.append(dict_obj[key])
        x.append(x_data)
    y = []
    for dict_obj in data:
        y_data = []
        for key in y_field:
            y_data.append(dict_obj[key])
        y.append(y_data)
    # return as numpy array
    x = np.asarray(x, np.float32)
    # normalize data
    #x = normalize_data(x)
    y = np.asarray(y, np.float32)
    #print(x)
    #print(y)
    return x, y


def normalize_data(x):
    for key in normalize_data_name:
        col_index = x_field.index(key)
        max, min = x[:, col_index].max(), x[:, col_index].min()
        #print(max, min)
        normalize_max_min.append((max,min))
        x[:, col_index] = (x[:, col_index]-min)/(max-min)
    return x


# decreasing the acceptable feedback
def amplify_feedback(data):
    feedback = []
    for dict_obj in data:
        feedback.append(dict_obj['feedback'])

    if (replace_acceptable is True):
        i = 0
        while(i < len(feedback)-1):
            if (feedback[i] != "acceptable"):
                break
            i += 1
        for j in range(0, i):
            feedback[j] = feedback[i]

        while(i < (len(feedback)-1)):
            if (feedback[i] != "acceptable"):
                j = i + 1
                while (True):
                    if (j > len(feedback)-1):
                        i = j
                        break
                    if (feedback[j] == "acceptable"):
                        feedback[j] = feedback[i]
                    else:
                        i = j - 1
                        #feedback[i-1] = feedback[i]
                        break
                    j += 1
            i += 1
    else:
        i = 0
        while(i < (len(feedback)-1)):
            if (feedback[i] != "acceptable"):
                for j in range(1, feedback_amplifier+1):
                    if (i+j > len(feedback)-1):
                        i = i+j
                        break
                    if (feedback[i+j] == "acceptable"):
                        feedback[i+j] = feedback[i]
                    else:
                        i = i+j
                        break
            i += 1
    i = 0
    for dict_obj in data:
        dict_obj['feedback'] = feedback[i]
        i += 1
    return data

# extract data from the env_training_data folder
def extract_data():
    datapack = []
    for i in range(1, num_of_paths()+1):
        datapack.append(get_data('env_training_data/env_data_'+str(i)+'.json', 'datapack'))
    data = []
    for pack in datapack:
        for dict_obj in pack:
            data.append(dict_obj)

    extract_data = []
    for pack in data:
        value = {}
        for key in data_name:
            value[key] = pack[key]
        extract_data.append(value)
    return extract_data


def process_data(data):
    # extract feedback and change to Enum name first
    feedback = []
    for dict_obj in data:
        dict_obj['set_temp'] -= 17
        #dict_obj['set_fanspeed'] -= 1
        str_feedback = dict_obj['feedback']
        str_feedback = str_feedback.lower()
        str_feedback = str_feedback.replace(' ', '_')
        '''
        if (str_feedback == "very_cold"):
            str_feedback = "cold"
        elif (str_feedback == "very_hot" or str_feedback == "a_bit_hot"):
            str_feedback = "hot"
        '''
        # change feedback name to number
        feedback.append(Feedback[str_feedback].value)
    i = 0
    for num in feedback:
        data[i]['feedback'] = num
        i += 1
    return data


def create_points(temp_hum_pair, color):
    points = []
    for pair in temp_hum_pair:
        point = {'interior': {'label': 'Interior',
                               'style': {'color': color,
                                         'marker': 'o', 'markersize': 3},
                               'xy': (pair[0], pair[1])}}
        points.append(point)
    return points

def my_clustering_mnist(X, y, n_clusters):
    # =======================================
    # Complete the code here.
    # you need to
    #   1. Cluster images into n_clusters clusters using the k-means implemented by yourself or the one provided in scikit-learn.
    #
    #   2. Plot centers of clusters as images and combine these images in a single figure.
    #
    #   3. Return scores like this: return [score, score, score, score]
    # =======================================
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit_predict(X)
    '''
    data = np.zeros((X.shape[0], 3))
    data[:,0] = X[:,0]*(normalize_max_min[0][0]-normalize_max_min[0][1])+normalize_max_min[0][1]
    data[:,1] = X[:,1]*(normalize_max_min[1][0]-normalize_max_min[1][1])+normalize_max_min[1][1]
    data[:,2] = kmeans.labels_
    '''
    plt.scatter(X[:, 1], X[:, 2], c=kmeans)
    plt.show()
    '''
    # Load default style:
    custom_style = {
        "figure": {
            "title": "Thermal Comfort Zone",
        },
        "limits": {
            "range_temp_c": [10, 30],
        },
        "chart_params": {
            "with_constant_rh": True,
            "with_constant_v": False,
            "with_constant_h": True,
            "with_constant_wet_temp": False,
            "with_zones": False
        }
    }

    color = [[1.0, 0, 0, 0.9],[1.0, 0.4, 0.4, 0.9],[1.0, 0.8, 0.8, 0.9],[0.592, 0.745, 0.051, 0.9],[0.6, 0.8, 1.0, 0.9],[0.4, 0.698, 1.0, 0.9],[0.0, 0.502, 1.0, 0.9]]
    chart = PsychroChart(custom_style)
    chart.plot(ax=plt.gca())

    for i in range(n_clusters):
        temp_hum_pair = data[np.where(data[:,2] == i)]
        temp_hum_pair = temp_hum_pair[:,0:2].tolist()
        points = create_points(temp_hum_pair, color=[random.random(),random.random(),random.random(),0.9])
        for point in points:
            chart.plot_points_dbt_rh(point)
    plt.show()
    '''
    return [0,0,0,0]
    '''
    ari_score = metrics.adjusted_rand_score(y, kmeans.labels_)
    mri_score = metrics.adjusted_mutual_info_score(y, kmeans.labels_)
    v_measure_score = metrics.v_measure_score(y, kmeans.labels_)
    avg_silhouette_score = metrics.silhouette_score(X, kmeans.labels_, metric='euclidean')
    return [ari_score,mri_score,v_measure_score,avg_silhouette_score]
    '''

def main():
    X, y = get_x_y()
    data = pd.DataFrame(columns=['temp','hum','body','outdoor_temp','outdoor_hum','set_fanspeed'], index=[i for i in range(len(X))])
    i = 0
    for row in data.index:
        data.loc[row, 'temp':'set_fanspeed'] = X[i,:]
        i += 1
    print(data)
    print("x shape = {}".format(X.shape))
    y = y[:,0]
    print("y shape = {}".format(y.shape))
    scaled_data = preprocessing.scale(data.T)
    pca = PCA()
    pca.fit(scaled_data)
    pca_data = pca.transform(scaled_data)
    per_var = np.round(pca.explained_variance_ratio_*100, decimals=1)
    labels = ['PC'+str(x) for x in range(1, len(per_var)+1)]

    plt.bar(x=range(1, len(per_var)+1), height=per_var, tick_label=labels)
    plt.ylabel('Percentage of Explained Variance')
    plt.xlabel('Principal Component')
    plt.title('Screen Plot')
    plt.show()

    pca_df = pd.DataFrame(pca_data, index=['temp','hum','body','outdoor_temp','outdoor_hum','set_fanspeed'], columns=labels)

    plt.scatter(pca_df.PC1, pca_df.PC2)
    plt.title('PCA Graph')
    plt.xlabel('PC1 - {0}%'.format(per_var[0]))
    plt.ylabel('PC2 - {0}%'.format(per_var[1]))

    for sample in pca_df.index:
        plt.annotate(sample, (pca_df.PC1.loc[sample], pca_df.PC2.loc[sample]))

    plt.show()

#    print('We need', pca.n_components_, 'dimensions to preserve 0.9 POV')
#    print(pca.explained_variance_)
    # Clustering

    #range_n_clusters = [2,3,4,5,6,7]
    range_n_clusters = []
    ari_score = [None] * len(range_n_clusters)
    mri_score = [None] * len(range_n_clusters)
    v_measure_score = [None] * len(range_n_clusters)
    silhouette_avg = [None] * len(range_n_clusters)

    for n_clusters in range_n_clusters:
        i = n_clusters - range_n_clusters[0]
        print("Number of clusters is: ", n_clusters)
        [ari_score[i], mri_score[i], v_measure_score[i], silhouette_avg[i]] = my_clustering_mnist(X, y, n_clusters)
        print('The ARI score is: ', ari_score[i])
        print('The MRI score is: ', mri_score[i])
        print('The v-measure score is: ', v_measure_score[i])
        print('The average silhouette score is: ', silhouette_avg[i])

    ari_score_plot = plt.plot(range_n_clusters, ari_score,label="ari_score")
    mri_score_plot = plt.plot(range_n_clusters, mri_score,label="mri_score")
    v_measure_score_plot = plt.plot(range_n_clusters, v_measure_score,label="v_measure_score")
    silhouette_avg_plot = plt.plot(range_n_clusters, silhouette_avg,label="silhouette_avg")
    plt.legend()
#    plt.show()


if (__name__ == '__main__'):
    main()
