# -*- coding: utf-8 -*-
"""Challenge_AprendizajeAutomatico.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1U3iSqvzW3fdUuYL3sy3UeXAr-ruJgjlM

<div class="title">Practical Assignment: Supervised Learning</div>
<div class="subtitle">Machine Learning</div>
<div class="author">Carlos María Alaíz Gudín - Universidad Autónoma de Madrid</div>

---

<div style="font-size: large; font-weight: bold; margin-left: 6em;">
    <p>Names: <u>Jose Maria Casanova y Jonatan Rodriguez</u>
    <p>Team Number: <u>6</u>
</div>

# **Initial Configuration**

This cell defines the configuration of Jupyter Notebooks.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%html
# <head><link rel="stylesheet" href="style.css"></head>

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
# %load_ext autoreload
# %autoreload 2

"""This cell imports the packages to be used (all of them quite standard except for `utils`, which is provided with the notebook."""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from sklearn.metrics import accuracy_score, balanced_accuracy_score

########################################
# Any other needed package can be imported here:

########################################

from utils import plot_dataset_clas

matplotlib.rc('figure', figsize=(15, 5))
seed = 123
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV,learning_curve
import warnings
warnings.filterwarnings('ignore')

from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MinMaxScaler

from sklearn.linear_model import SGDClassifier

from sklearn.neighbors import KNeighborsClassifier

from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

from sklearn.linear_model import Perceptron
from utils import plot_dataset_clas, plot_linear_model_clas, plot_perceptron_evo_iter
from sklearn.neural_network import MLPClassifier

from sklearn import tree
from sklearn.tree import export_graphviz
from six import StringIO
from IPython.display import Image
import pydotplus

from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

import lightgbm as lgb

"""# Preliminaries

## Introduction

This practical assignment is designed as a **Kaggle competition**.

Specifically, a **multiclass classification** dataset will be used, so that each team will compete to improve their predictions over an unlabeled partition of the dataset.

It is important to remark that **the grades will not depend on the obtained ranking**, but on the different approaches used to tackle the problem, on the design of the experiments and on the analysis of the results.

## Rubric

The following aspects will be taken into account when evaluating the assignment.


* Analyse the data.


* Preprocess the features automatically using *pipelines*.


* Adjust the hyper-parameters with a validation stage.


* Try different models to improve the performance, at least:
    * (Regularized) Logistic Regression.
    * SVC.
    * ANNs.


* Try interpretable models to check the important features (e.g. Lasso).


* Submit the prediction several times (the evolution of the performance will be also considered).


* Any other approach that may improve either the performance or interpretability of the model (e.g. feature selection, ensembles...).


* Analyse the results obtained after each experiment, and make decisions following the conclusions.

## Utilities

Some utilities are given next as a starting point, but the teams can defined any other tools that they may need.

### Team Number

The **number of the team** should be inserted here, so that the file of predictions has the appropriate name.
"""

########################################
# The team number should be inserted here:
team_number = 6
########################################

"""### Evaluation of the Model

The following function evaluates a multiclass model (already fitted), computing and showing the accuracy and balanced accuracy over both the training and test partitions.
"""

def evaluate_model(model, X_tr, y_tr, X_te, y_te, print_table=True):
    y_tr_p = model.predict(X_tr)
    y_te_p = model.predict(X_te)

    er_tr = [accuracy_score(y_tr, y_tr_p), balanced_accuracy_score(y_tr, y_tr_p)]
    er_te = [accuracy_score(y_te, y_te_p), balanced_accuracy_score(y_te, y_te_p)]

    ers = [er_tr, er_te]
    headers=["Acc", "Bal. Acc"]

    if print_table:
        print("{:>15}".format(""), end="")
        for h in headers:
            print("{:>15}".format(h), end="")
        print("")

        headersc = ["Train", "Test"]

        cnt = 0
        for er in ers:
            hc = headersc[cnt]
            cnt = cnt + 1
            print("{:<15}".format(hc), end="")

            for e in er:
                print("{:15.2f}".format(e), end="")
            print("")

    return ers

"""## Submission of the Predictions

The following function saves the predictions on the **challenge partition** to a file with syntax `Team_TT_YYYYMMDD-HHMMSS.pred`, where `TT` stands for the team number, and `YYYYMMDD-HHMMSS` is a timestamp to distinguish the different submissions of a team.
"""

import time

def save_predictions(y_ch_p, n_preds=500):
    if (len(y_ch_p) != n_preds):
        print("Error saving the predictions, it should be a vector of %d lables" % n_preds)
    else:
        time_str = time.strftime("%Y%m%d-%H%M%S")
        np.savetxt("Team_{:02d}_{}.txt".format(team_number, time_str), y_ch_p, fmt="%d")

"""Once the prediction file has been generated, it can be uploaded to Moodle in the following [link](https://posgrado.uam.es/mod/assign/view.php?id=848775)

# Dataset

A real dataset will be tackled in this practical assignment.
In particular, the [fetal health](https://www.kaggle.com/andrewmvd/fetal-health-classification) dataset of Kaggle, that aims to classify the fetal health in three classes:
1. Normal.
2. Suspect.
3. Pathological.

The input data are a set of $21$ variables extracted from the cardiotocographies (CTGs).

## Load of the Dataset

This cell loads the data, in particular three partitions:
1. A training partition, given by `X_tr` and `y_tr`, to train (and validate) the models.
2. A test partition, given by `X_te` and `y_te`, to estimate the performance of the model.
3. A challenge partition, given by `X_ch`. The real labels are unknown, and hence the predictions should be submitted to know the real performance of the model.
"""

rootf = "./Data/fetal_health"

X_tr = np.loadtxt(rootf + "_tr.dat")
X_te = np.loadtxt(rootf + "_te.dat")
X_ch = np.loadtxt(rootf + "_ch.dat")

y_tr = np.loadtxt(rootf + "_tr.lab")
y_te = np.loadtxt(rootf + "_te.lab")

features = [line.rstrip('\n') for line in open("./Data/fetal_health.head")]
n_features = len(features)

"""## Initial  Analysis

Plot of the data over the first two features.
"""

import pandas as pd
df = pd.DataFrame(X_tr,columns=features)
df["Salida"]= y_tr
df
#Dado que solo tenemos 21 variables no consideramos necesario la reducción de dimensiones

df.dtypes
#Podemos comprobar como todos los valores de los datos son floats

df.describe()
#Aquí podemos ver medias, desviaciones estándar y cuantas entradas hay por feature.

import seaborn as sns

f, ax = plt.subplots(figsize=(10, 8))
corr = df.corr()
sns.heatmap(corr,annot=True,
            xticklabels=corr.columns.values,
            yticklabels=corr.columns.values)
plt.show()

"""Aquí podemos ver el heatmap de las features y podemos comprobar como de relacionadas están unas con otras.
La más relacionada con la salida corresponde a "prolonged decelerations"
"""

plot_dataset_clas(X_tr, y_tr)
plt.xlabel(features[0])
plt.ylabel(features[1])
plt.legend(["Normal", "Suspect/Pathological"])
plt.axis("auto")
plt.show()

"""Balance of the dataset."""

for lab in np.unique(y_tr):
    n_sam = np.sum(y_tr == lab)
    print("Class {}: {:3d} samples ({:5.2f}%)".format(lab, n_sam, 100.0 * n_sam / len(y_tr)))

"""# Metodos con las muestras iniciales

## Experimento 1: Regresión logística
"""

#Modelo de regresión lineal general que toma los valores de forma binomial.

modelo_regresion_logistica = linear_model.LogisticRegression()
modelo_regresion_logistica.fit(X_tr,y_tr)

d = {} # Creamos un diccionario para que nos guarde los datos de evaluación
#Evaluación del modelo
d["Modelo de regresión logistica"]=evaluate_model(modelo_regresion_logistica, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=modelo_regresion_logistica.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""El resultado da un porcentaje del 85% de predicción. Aunque los datos son buenos, si nos fijamos en balanced_accuracy podemos ver como estos resultados empeoran.  Creemos que esto se debe al desbalanceo de clases lo que hace que obtengamos peores resultados que un modelo dummy.

## Experimento 2: Regresión logística. Selección de hiperparámetros
"""

# Modelo de regresión lógistica con parametros personalmente modificados. Estos parametros buscan la mejor predicción en un rango determinado

parameters = {
    'penalty' : ['l1','l2'],
    'C'       : np.logspace(-3,3,7),
    'solver'  : ['newton-cg', 'lbfgs', 'liblinear'],
}
# se añade un 'penalty' o regulador: 'l1' se refiere a regularización L1 (Lasso) y 'l2' se refiere a regularización L2 (Ridge).
# se añade C, la inversa de la fuerza de regulación en un rango de 10^-3 - 10^3 cogiendo 7 valores de estos espaciados logaritmicamente.
# solver: añade los 3 algoritmos de regresión logistica.

# se procede a la implementación de los parametros y al entrenamiento.
logreg = LogisticRegression()
clf = GridSearchCV(logreg,param_grid = parameters,scoring='accuracy',cv=10)
clf.fit(X_tr,y_tr)

# Evaluación del modelo
d['Modelo de regresión logística mejorado']=evaluate_model(clf, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Genera una predicción mejor que el anterior con una precisión del 90%  y una balance accuracy del 78%. Podemos comprobar como el modelo ha mejorado gracias a la selección de hiperparámetros aunque supera por muy poco al modelo dummy.

## Experimento 3: Multinomial Naives Bayes (Normalizado)
"""

# El algoritmo es una variante de Naive Bayes. Se establece calculando la probabilidad de
# ocurrencia de un dato.

scaler = MinMaxScaler()#Hemos tenido que normalizarlo dada la presencia de número negativos
X_tr = scaler.fit_transform(X_tr)
X_te = scaler.transform(X_te)

clf_MNB =  MultinomialNB().fit(X_tr , y_tr)
predicted = clf_MNB.predict(X_te)

# Evaluación del modelo
d['Modelo Multinomial Naives Bayes']=evaluate_model(clf_MNB, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Al igual que en los casos anteriores, obtenemos un accuracy decente pero la balanceada pierde mucho dado el desbalanceo de clases.

## Experimento 4: Multinomial Naives Bayes (Normalizado). Selección de hiperparámetros.
"""

#Parametros los cuales alpha es modificado de tal manera que guardará la mejor predicción.

parameters = { 'alpha': (1, 0.1, 0.01, 0.001, 0.0001, 0.00001)  }

clf_MNB2= GridSearchCV( MultinomialNB(), parameters)
clf_MNB2.fit(X_tr,y_tr)
y_ch=clf_MNB2.predict(X_ch)
#save_predictions(y_ch, n_preds=500)

#Evaluación del modelo
d['Modelo Multinomial Naives Bayes mejorado']=evaluate_model(clf_MNB2, X_tr, y_tr, X_te, y_te, print_table=True)

"""Los resultados mejoran levemente pero no son suficientes ya que tiene un balanced accuracy del 42%.

## Experimento 5: Clasificador SGD
"""

# EL algoritmo SGDClassifier utiliza un método de descenso de gradiente estocástico para
# encontrar los pesos óptimos que mejor se ajusten a datos de entrenamiento, minimizando así
# a función de perdida. Este método es mejor para conjunto de datos grandes y multiclase.

clf_SGD =  SGDClassifier().fit(X_tr, y_tr)

#Evaluación del modelo
d['Modelo de clasificador SGD']=evaluate_model(clf_SGD, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf_SGD.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Este modelo ha generado mejores predicciones que el anterior con una precisión del 44% y un balanceada del 62%. Siendo este una predicción bastante mala. Aunque curioso que sea mejor en la balanceada.

## Experimento 6: Clasificador SGD mejorado
"""

# Parámetros modificados para mejorar la calidad del modelo.
# Especifica la función de perdida, penalización y intercepción.
# Después compara los resultados para coger el mejor y ajusta los parametros.
parameters={"loss":["hinge", #perdida de bisagra
                    "log_loss", #perdida logarítmica
                    "log", #perdida regresión logística
                    "modified_huber",
                    "squared_hinge", # perdida de bisagra cuadratica
                    "perceptron",
                    "squared_error", # error cuadrático
                    "huber",
                    "epsilon_insensitive",
                    "squared_epsilon_insensitive"],
            "penalty":["l2", "l1", "elasticnet", None], # compara las funciones de penalización
                                                        # l1 y/o l2 ya explicados anteriormente
            "fit_intercept": [True, False] #  ajusta la intercepción usando ambos casos.
            }
clf_SGD2= GridSearchCV(SGDClassifier(),parameters)
clf_SGD2.fit(X_tr,y_tr)

#Evaluacion del modelo
d['Modelo de clasificador SGD mejorado']=evaluate_model(clf_SGD2, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf_SGD2.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Este modelo ha generado una precisión del 86% y balanceada del 67% una mejoría leve al anterior modelo. El balance para el test es bastante bajo lo que le hace un modelo malo

## Experimento 7: KNN vecinos más cercanos
"""

#Algoritmo de K vecinos más cercanos

k_values = range(1,15)
# k_values es un rango de valores del 1 al 14 (los vecinos más cercanos, k-values)

param_grid = {'n_neighbors': k_values}
# param_grid especifica los hiper-parámetros que se utilizarán para hacer una validación cruzada

kNN_model=KNeighborsClassifier()
grid = GridSearchCV(kNN_model, param_grid, cv = 3, scoring = 'accuracy')
grid.fit(X_tr,y_tr)
print(grid.best_params_)

kNN=KNeighborsClassifier(n_neighbors=5)
modelo_knn=kNN.fit(X_tr,y_tr)
y_pred=modelo_knn.predict(X_te)
preci=accuracy_score(y_te, y_pred)
preci

#Evaluacion del modelo
d['Modelo de KNN vecinos proximos']=evaluate_model(modelo_knn, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=modelo_knn.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Se determinó que el mejor valor de K son 5 eso quiere decir que se necesitan 5 vecinos para determinar el valor predictivo más correcto. Con esto se llega a una exactitud del 92%. El balanced accuracy es de un 75% para la prueba siendo este mejor que el anterior modelo con una leve mejoría. Dada la diferencia entre train y test intuimos que exite overfitting en el train

## Experimento 8: Perceptrón (Red neuronal)
"""

#El siguiente modelo que vamos a probar es el perceptrón multicapa. Los parámetros que probaremos en el gridsearch son los siguientes:

param_grid= { "hidden_layer_sizes":[1,2,5,10,25,50,100,200], #Neuronas que tendrá la capa intermedia
             "activation":["logistic","tanh","relu","identity"], # Función de activación. "identity" : función lineal , "logistic" : función sigmoide, "tanh" : función tangente hiperbólica y "relu" : unidad lineal rectificada.
            "learning_rate": ["adaptive","constant","invscaling"],# Tasa de aprendizaje utilizada para ajustar los pesos del modelo
             "max_iter":[1000]} # Número máximo de iteraciones

model=MLPClassifier()
clf_MLP=GridSearchCV(model,param_grid)
clf_MLP.fit(X_tr,y_tr)

#Evaluación del modelo
d['Modelo de perceptrón multicapa']=evaluate_model(clf_MLP, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf_MLP.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Hace una predicción con un accuracy del 97% y una balanced accuracy para la prueba del 74% bastante más alto que los modelos anteriores pero insuficiente.

## Experimento 9: Red neuronal mejorada
"""

# Este modelo es exactamente igual al anterior pero determinando cuales son los mejores parametros
# con un bucle for en vez de que lo haga automaticamente el programa.

n_neuronas=[1,2,5,10,25,50,100,200] # establece el número de neuronas de la capa intermedia
# la función de activación utilizada en las capas ocultas de la red neuronal
f_act=["logistic", # función sigmoide, produce una salida en el rango de 0 a 1
       "tanh", # función tangente hiperbólica produce una salida en el rango de -1 a 1
       "relu", # función de activación lineal rectificada (red neuronal profunda)
       "identity"] # sin transformación
# parámetro representa el tipo de tasa de aprendizaje utilizada
t_apre=["adaptive", # se ajusta adaptativamente
        "constant", # se ajusta constantemente
        "invscaling"] # se reduce gradualmente a lo largo del tiempo

comb={}
# bucle for que establece los resultados de los parametros para predecir.
for n in n_neuronas:
    for f in f_act:
        for t in t_apre:

            clf_MLP2 = MLPClassifier(hidden_layer_sizes=(n,),activation=f,random_state=0,early_stopping=True,learning_rate=t, max_iter=2000).fit(X_tr, y_tr)

            clave= str(n)+" neuronas "+"func. de act: "+f + " tasa aprend. " + t

            clf_MLP2.predict_proba(X_te)
            clf_MLP2.predict(X_te)
            comb[clave]=clf_MLP2.score(X_te, y_te)

#Establece el mejor parámetro para estos datos

for x in comb.keys():
  if comb[x]== max(comb.values()):
    print(x,comb[x])

# una vez se detectan los mejores parametros se escriben y se hace el modelo.

clf_MLP2 = MLPClassifier(hidden_layer_sizes=(200,),activation="relu",random_state=0,early_stopping=True,learning_rate="adaptive", max_iter=2000).fit(X_tr, y_tr)
clf_MLP2.fit(X_tr, y_tr)

# Evaluación del modelo
d['Modelo de perceptrón multicapa mejorada']=evaluate_model(clf_MLP2, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf_MLP2.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""La predicción ha sido bastante peor que la anterior. Con una balanced accuracy del 69%

## Experimento 10: Árbol clasificatorio
"""

# El algoritmo busca de forma recursiva las mejores características y umbrales para dividir el
# conjunto de datos en subconjuntos, se puede utilizar para predecir la clase de una nueva
# instancia siguiendo el camino desde la raíz del árbol hasta una de sus hojas.

# hiper parámetros que sirven como validación cruzada y así mejorar la calidad de estos.
max_depth = np.arange(1, 25)
min_samples_leaf = [1, 5, 10,15]

# prueba cada uno de estos parámetros para llegar a un punto óptimo.
param_grid = { 'criterion':['entropy'], # lo que significa que se utiliza la ganancia de información basada en la entropía
              "min_samples_leaf":min_samples_leaf, # determina el número mínimo de subnodos por cada nodo
              'max_depth': max_depth} # Establece la profundidad o la cantidad máximas de niveles en el árbol.

dtree_model=tree.DecisionTreeClassifier()
dtree_model = GridSearchCV(dtree_model, param_grid, cv=3, scoring="accuracy")
dtree_model=dtree_model.fit(X_tr, y_tr)

# Evaluación del modelo
d['Modelo de Árbol clasificatorio']=evaluate_model(dtree_model, X_tr, y_tr, X_te, y_te, print_table=True)

"""Hemos conseguido un resultado del 100% tanto como de forma general y de forma balanceada. Lo que es un nivel de precisión muy bueno ya que hace una predición perfecta al menos para los datos de entrenamiento. Los datos de prediccion de test no han sido tan buenos con 82% en la balanceada. Existe overfitting"""

y_ch=dtree_model.predict(X_ch)
save_predictions(y_ch, n_preds=500)

my_model = dtree_model.best_estimator_
my_tree=my_model.fit(X_tr,y_tr)
dot_data = StringIO()
export_graphviz(my_tree, out_file=dot_data,
                filled=True, rounded=True,
                special_characters=True,feature_names = features,class_names=['Sano','Sospechoso',"Patológico"])

graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
graph.write_png('arbol.png') # representación gráfica del árbol
Image(graph.create_png())

"""Se hace la representación gráfica del árbol para determinar que caracteristica se acerca más al valor deseado. Aquí se puede observar que utiliza el abnormal short term variability como caracteristica principal. Se puede observar que en el heatmap creado que es la segunda caracteristica con más relación después utiliza para subdividir el arbol el prolonged decelerations para clasificar como sano. Este valor es el que tiene más relación con los datos de salida.

Graciás a este arbol de clasificacion, donde utiliza la entropia para clasificar, el numero de muestras y los valores de cada caracteristica para poder clasificarlo, ha podido llegar a un 100% de predición para el entrenamiento y un 92% para los de test.

## Experimento 11: Random Forest
"""

param_grid = {
    'n_estimators': [100, 200, 300],  # Número de árboles en el bosque
    'max_depth': [None,1, 5, 10],
    'min_samples_split': [2, 5, 10,15],
    'min_samples_leaf': [1, 2, 4,12]
}

rf = RandomForestClassifier(random_state=42)

grid_search_rf = GridSearchCV(estimator=rf , param_grid=param_grid, cv=5)
grid_search_rf.fit(X_tr, y_tr)

# Evaluación del modelo
d['Modelo de Random Forest']=evaluate_model(grid_search_rf, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=grid_search_rf.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Par el test ha generado un Balance de accuracy del 84% algo mayor que el de el arbol clasificatorio

# Comparación de todos los modelos anteriores

Creamos una tabla para poder diferenciar todos los modelos. Será ordenada segun su balance accuracy tanto como en training y test data.
"""

df_clasificadores = pd.DataFrame(d)

new_data = {}

for key, values in df_clasificadores.items():
    # Separar los valores de la lista en "Acc" y "Balance Acc"
    train_acc = values[0][0]
    train_balance = values[0][1]
    test_acc = values[1][0]
    test_balance = values[1][1]
    new_data[key] = {'train_acc': train_acc, 'train_balance_acc': train_balance, 'test_acc': test_acc, 'test_balance_acc': test_balance}

# dataframe de mayor a menor según el train accuracy
df_c = pd.DataFrame(new_data)
df_c = df_c.transpose()

print('Tabla ordenada según el balance de precisión del entrenamiento ')
df_c = df_c.sort_values(by='train_balance_acc', ascending=False)
df_c['train_balance_acc']

print('Tabla ordenada según el balance de precisión de la prueba ')
df_c = df_c.sort_values(by='test_balance_acc', ascending=False)
df_c['test_balance_acc']

"""Se puede observar que el modelo que ha generado mejor predicción ha sido el Modelo de clasificacion ramificado o *clasification tree* el cual tiene un nivel de precisión es un 100% en el train y 92% en el test.

# Metodos haciendo Upsampling

Dado el alto desajuste de las clases vamos a probar a hacer upsampling que consiste en el aumento de las muestras con un porcentaje menor de cada clase. Así lo que vamos a conseguir es que haya un número balanceado de muestras para evitar el overfitting

Hemos decidido coger los modelos que mejor resultados dieron en los anteriores metodos
"""

X_tr, y_tr = SMOTE().fit_resample(X_tr, y_tr)

"""## Experimento 1: Árbol clasificatorio

---


"""

max_depth = np.arange(1, 7)
min_samples_leaf = [1, 5, 10]

# prueba cada uno de estos parámetros para llegar a un punto óptimo.
param_grid = { 'criterion':['entropy'], # lo que significa que se utiliza la ganancia de información basada en la entropía
              "min_samples_leaf":min_samples_leaf, # determina el número mínimo de subnodos por cada nodo
              'max_depth': max_depth} # Establece la profundidad o la cantidad máximas de niveles en el árbol.

dtree_model2 = tree.DecisionTreeClassifier()
dtree_model2 = GridSearchCV(dtree_model2, param_grid, cv=3, scoring="accuracy")
dtree_model2 = dtree_model2.fit(X_tr, y_tr)

d2 = {} # Creamos un diccionario para los resultados de la segunda tanda de entrenamiento.
# Evaluacioón del modelo
d2['Modelo de Árbol clasificador']=evaluate_model(dtree_model2, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=dtree_model.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Nos da el que mejor hasta la fecha en porcentaje de precisión respecto al balance de los datos hechos predichos con el test. Eso nos da buena señal, eso si cabe destacar que tiene un porcentaje menor en precision con respecto a otros training data.

## Experimento 2: Random Forest

Vamos a hacer otra versión de Random Forest con diferentes hyperparametros
"""

param_grid = {
    'n_estimators': [100, 200, 300],   # estimaciones
    'max_depth': [None, 5, 10],  # maxima profundidaz
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf = RandomForestClassifier(random_state=42)

grid_search_rf3 = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, scoring='balanced_accuracy')
grid_search_rf3.fit(X_tr, y_tr)

# Evaluación del modelo
d2['Modelo de Random Forest']=evaluate_model(grid_search_rf3, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=grid_search_rf.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Como se puede observar tiene un porcentaje de accuracy del 100 en el training comparado con el 92% con el test y un accuracy balanceada del 86%.

## Experimento 3: Regresión Logística
"""

# Modelo de regresión lógistica con parametros personalmente modificados.

parameters = {
    'penalty' : ['l1','l2'],
    'C'       : np.logspace(-3,3,7),
    'solver'  : ['newton-cg', 'lbfgs', 'liblinear'],
}
# se añade un 'penalty' o regulador: 'l1' se refiere a regularización L1 (Lasso) y 'l2' se refiere a regularización L2 (Ridge).
# se añade C, la inversa de la fuerza de regulación en un rango de 10^-3 - 10^3 cogiendo 7 valores de estos espaciados logaritmicamente.
# solver: añade los 3 algoritmos de regresión logistica.

# se procede a la implementación de los parametros y al entrenamiento.
logreg = LogisticRegression()
modelo_rl = GridSearchCV(logreg,param_grid = parameters,scoring='balanced_accuracy',cv=10)
modelo_rl.fit(X_tr,y_tr)

# Evaluación del modelo
d2["Modelo de regresión logistica"]=evaluate_model(modelo_rl, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""El modelo de regresión logistica nos ha dado peores resultados para el entrenamiento y no tan malos resultados para el test.

## Experimento 4: Perceptron (red neuronal)
"""

param_grid= { "hidden_layer_sizes":[1,2,5,10,25,50,100,200], #Neuronas que tendrá la capa intermedia
             "activation":["logistic","tanh","relu","identity"], # Función de activación. "identity" : función lineal , "logistic" : función sigmoide, "tanh" : función tangente hiperbólica y "relu" : unidad lineal rectificada.
            "learning_rate": ["adaptive","constant","invscaling"],# Tasa de aprendizaje utilizada para ajustar los pesos del modelo
             "max_iter":[500,1000,2000]} # Número máximo de iteraciones

model=MLPClassifier()
clf_MLP2 = GridSearchCV(model,param_grid,scoring='balanced_accuracy',cv=10)
clf_MLP2.fit(X_tr,y_tr)

# Evaluación del modelo
d2['Modelo de perceptrón multicapa']=evaluate_model(clf_MLP2, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=clf_MLP.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""La red neuronal ha sido más lenta que la anterior y el nivel de precisión para el balance hecho con los datos de prueba es menor que lo hecho con la regresión logistica, aunque tenga un nive de precisión para el entrenamiento mayor el coste computacional no vale la pena.

## Experimento 5: KNN vecionos más cercanos
"""

k_values = range(1,15)
# k_values es un rango de valores del 1 al 14 (los vecinos más cercanos, k-values)

param_grid = {'n_neighbors': k_values}
# param_grid especifica los hiper-parámetros que se utilizarán para hacer una validación cruzada

kNN_model=KNeighborsClassifier()
grid = GridSearchCV(kNN_model, param_grid, cv = 3, scoring = 'accuracy')
grid.fit(X_tr,y_tr)
print(grid.best_params_)

kNN=KNeighborsClassifier(n_neighbors=5)
modelo_knn2=kNN.fit(X_tr,y_tr)
y_pred=modelo_knn2.predict(X_te)
preci=accuracy_score(y_te, y_pred)
preci

d2['Modelo de KNN vecinos proximos']=evaluate_model(modelo_knn2, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=modelo_knn2.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Existe overfitting en los datos de test y además no supera demasiado al modelo dummy.

## Experimento 6: clasificador de impulso de gradiente LightGBM

GBM es una técnica de aprendizaje automático supervisado que se utiliza para problemas de clasificación y regresión. Utiliza el algoritmo de boosting para combinar múltiples árboles débiles en un modelo fuerte. Los árboles débiles se construyen de manera secuencial, y cada árbol se enfoca en corregir los errores residuales cometidos por los árboles anteriores.
"""

lgbm = lgb.LGBMClassifier()

param_grid = {
    'num_leaves': [5,10,20, 30, 40], # numero de ramas/hojas
    'max_depth': [2,5, 10, -1,20,-2], # número máximo de profundidad del arbol. Son parametros en rango para determinar cual es el mejor.
    'learning_rate': [0.001]
}



grid_search_lgbm = GridSearchCV(lgbm, param_grid=param_grid, scoring="balanced_accuracy", cv=16)
grid_search_lgbm.fit(X_tr, y_tr)

d2['Modelo de clasificador LightGBM']=evaluate_model(grid_search_lgbm, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=grid_search_lgbm.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""El accuracy de este metodo es bastante alto con un 91% y 87% para el balanceado del test por lo cual es el que menos overfitting tiene. Por ahora es el mejor de todos pero con muy poca diferencia con el arbol y el random forest.

## Experimento 7: clasificador de impulso de gradiente (GBC)

En terminos de eficacia el GBC basado en GBM se diferencia en eficacia con LightGBM. Aunque es menos eficiente puede dar resultados mejores por eso hemos seleccionado este metodo para probar si es más preciso que el resto
"""

from sklearn.ensemble import GradientBoostingClassifier
gbc = GradientBoostingClassifier()
param_grid = {
    'n_estimators': [100, 200, 300],
    'learning_rate': [0.1, 0.01, 0.001],
    'max_depth': [None, 3, 4, 5]
}
# Ajustar el modelo en los datos de entrenamiento
grid_search_g = GridSearchCV(estimator=gbc, param_grid=param_grid, scoring="balanced_accuracy", cv=5)
grid_search_g.fit(X_tr, y_tr)

d2['Modelo de clasificador GBM']=evaluate_model(grid_search_g, X_tr, y_tr, X_te, y_te, print_table=True)

y_ch=grid_search_g.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Lo impportante de este es que tiene mucho mejor balance en el test que los modelos anteriores con un 86% pero muy parizo con random forest

## Comparación de todos los modelos

Añadimos los 2 arboles con mejor resultado de la anterior para así poder compararlos
"""

# Añadimos los 2 arboles
d2['Modelo de Árbol Clasificatorio_noUp']=evaluate_model(dtree_model, X_tr, y_tr, X_te, y_te, print_table=True)
d2['Modelo de Random Forest_nUp']=evaluate_model(grid_search_rf, X_tr, y_tr, X_te, y_te, print_table=True)

df_clasificadores2 = pd.DataFrame(d2)

new_data = {}

for key, values in df_clasificadores2.items():
    # Separar los valores de la lista en "Acc" y "Balance Acc"
    train_acc = values[0][0]
    train_balance = values[0][1]
    test_acc = values[1][0]
    test_balance = values[1][1]
    new_data[key] = {'train_acc': train_acc, 'train_balance_acc': train_balance, 'test_acc': test_acc, 'test_balance_acc': test_balance}

# dataframe de mayor a menor según el train accuracy
df_c2 = pd.DataFrame(new_data)
df_c2 = df_c2.transpose()

print('Tabla ordenada según el balance de precisión del entrenamiento ')
df_c2 = df_c2.sort_values(by='train_balance_acc', ascending=False)
df_c2['train_balance_acc']

print('Tabla ordenada según el balance de precisión de la prueba ')
df_c2 = df_c2.sort_values(by='test_balance_acc', ascending=False)
df_c2['test_balance_acc']

"""Como se puede observar para los datos de training con mas accuracy Random Forest es el mejor ya que tiene un 100% seguido del clasificador de impulso de gradiente con una posicion igual.

Para los datos de la prueba en cambio, el balance de precisión en lightGBM lo convertiría en el mejor ya que en el la diferencia entre la prueba y el entrenamiento no es muy alta y ya que la prueba es más importante consideramos que el  modelo de impulso de gradiente light es el mejor modelo de todos.

También nos damos cuenta de que estos modelos  son mejores que los utilizados sin el upsampling entonces llegamos a la conclusion que para este tipo de datos es importante hacer un upsampling e igualar así las clases minoritarias con las mayoritarias.

## Random Forest. Feature Selection + upsampling

Vamos a crear un modelo (Random Forest )que use aquellas features que superen el umbral de importancia. Esta selección la hacemos con otro random forest.
"""

clf = RandomForestClassifier()

clf.fit(X_tr, y_tr)

importance = clf.feature_importances_
sorted_indices = importance.argsort()[::-1]
top_features = sorted_indices

X_train_selected = X_tr[:, top_features]
X_test_selected = X_te[:, top_features]

#Hemos ordenado las características según la importancia de estas

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10],
    'min_samples_split': [2, 4, 8]
}

grid_search = GridSearchCV(clf, param_grid, cv=5, scoring='balanced_accuracy')
grid_search.fit(X_train_selected, y_tr)
best_params = grid_search.best_params_

model = RandomForestClassifier(**best_params)
model.fit(X_train_selected, y_tr)

#Y con este orden de características entrenamos el modelo. También hemos intentado quedarnos solo con aquellas características más explicativas,
#pero probando diferentes combinaciones hemos podido comprobar que perdiamos calidad si quitabamos algo

evaluate_model(model, X_train_selected, y_tr,X_test_selected, y_te, print_table=True)

y_ch=model.predict(X_ch)
save_predictions(y_ch, n_preds=500)

"""Como podemos comprobar este es el modelo que mejores resultados obtenemos. Todo esto se debe a todo el preprocesado previo al entrenamiento del modelo"""