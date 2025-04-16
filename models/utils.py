import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kendalltau
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import explained_variance_score


plt.rcParams['font.family'] = 'DejaVu Sans'

def plot_scatter(x1,y1,x2=None,y2=None,bound=None,name = ['Title','x','y'],label = ['',''],color=['blue','red']):
    print('plot_scatter')
    fig = plt.figure(figsize=(8, 8))
    plt.scatter(x1, y1, c=color[0],s=4,alpha=0.5,label=label[0])
    if x2 is not None:
        plt.scatter(x2, y2, c=color[1],s=4,alpha=0.7,label=label[1])
    if(bound == None):
        bound = [min(x1)-0.2*(max(x1)-min(x1)),max(x1)+0.2*(max(x1)-min(x1))]
    plt.plot([bound[0], bound[1]], [bound[0], bound[1]], 'k--', lw=1,alpha=0.5)  # 添加一条对角线


    r2 = r2_score(x1, y1)
    mse = mean_squared_error(x1,y1)

    textstr = f'{label[0]} \nR²    = {r2:.3f}\nMSE = {mse:.3f}'
    if x2 is not None:
        r2_2 = r2_score(x2, y2)
        mse_2 = mean_squared_error(x2,y2)

        textstr += f'\n\n{label[1]} \nR²    = {r2_2:.3f}\nMSE = {mse_2:.3f}'

    plt.text(0.02, 0.8, textstr, transform=plt.gca().transAxes, fontsize=16,
         verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    
    plt.title(name[0])
    plt.xlabel(name[1])
    plt.ylabel(name[2])
    plt.xlim(bound[0],bound[1])
    plt.ylim(bound[0],bound[1])
    plt.legend(fontsize=16)
    plt.grid(True)
    plt.show()
    return fig

def tau(list1,list2):
    return kendalltau(list1,list2)

def evaluation(y_pred,y_test):

    r2 = r2_score(y_test, y_pred)
    print(f'R² Score: {r2}')

    mse = mean_squared_error(y_test, y_pred)
    print(f'MSE: {mse}')

    # explained_variance = explained_variance_score(y_test, y_pred)
    # print(f'Explained Variance: {explained_variance}')

    # kendalltau = tau(y_pred,y_test)
    # print('Kendalltau:',kendalltau)


if __name__ == "__main__":
    evaluation(
        [1,2,3,4],
        [5,6,7,8]
    )