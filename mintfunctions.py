import seaborn as sns
from matplotlib.gridspec import GridSpec
from datetime import datetime
import calendar
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def generate_pdf(df,pdfdir = '', figdir = r'./figures',yearly_exclude_category = None, spending_drop_categories = ['Income', 'Transfer','Reimbursement','Credit Card Payment','Loans']):
    '''
    DESCRIPTION
    Produces a pdf showing the following figures:
    (1) Monthly breakdown of income & expenses by year
    (2) Heatmap of monthly spending by category
    (3) Pie chart showing latest months spending
    
    INPUT
    df = pandas dataframe, processed dataframe showing MINT input
    savedir = string, directory to save .pdf output. Default is r'./figures' subdirectory
    yearly_exclude_category = string, Overall Category to exclude from final yearly expense plot.  Allows user to find yearly expenses excluding a single category of expenses - must match name of Overall Category.  Default is None.
    drop_categories = list, overall categories to drop from spending dataframe.  Default is ['Income', 'Transfer','Reimbursement','Credit Card Payment','Loans']
    
    OUTPUT
    pdf of spending in output directory
    '''
    
    #CREATE SPENDING AND INCOME DATAFRAMES
    df_income = df.loc[df['Overall_Category']=='Income'].copy()
    df_spending = df.loc[~df['Overall_Category'].isin(spending_drop_categories)].copy()
    df_spending = df_spending.loc[~df_spending['Account Name'].isin(['401(k) Plan'])]
    
    #Create variables that document current month and year for pdf generation
    currentyear = datetime.now().year
    currentmonth = datetime.now().month

    #PDF Directory
    if pdfdir == '':
        pdfpath = '{}_{}_Report.pdf'.format(currentmonth,currentyear)
    else:
        pdfpath = pdfdir + '{}_{}_Report.pdf'.format(currentmonth,currentyear)
        
    #Generate Plots and PDF        
    with PdfPages(pdfpath) as pdf:
        for year in sorted(df_spending['YYYY'].unique(),reverse=True):
            #Expense and income plot
            df_temp = pd.concat([df_spending.loc[df_spending['YYYY']==year].groupby(['YYYY','MM']).sum()['Amount'].rename('Expenses')*-1,
                                 df_income.loc[df_income['YYYY']==year].groupby(['YYYY','MM'])['Amount'].sum().rename('Income')],axis=1)
            #Get x-axis labels
            labels = []
            for idx,row in df_temp.iterrows():
                labels.append('{}-{}'.format(calendar.month_abbr[idx[1]],str(idx[0])[-2:]))

            #Initialize figure
            fig=plt.figure(figsize=(20,20))
            gs=GridSpec(2,2) # 2 rows, 3 columns
            ax1=fig.add_subplot(gs[0,:]) # First row, all
            ax2=fig.add_subplot(gs[1,0]) # First row, first column
            ax3=fig.add_subplot(gs[1,1]) # First row, second column

            axbar= df_temp.plot.bar(ax=ax1,width=0.75,color=['salmon','springgreen'],edgecolor=['darkred','darkgreen'])

            #Add bar labels to plot
            rects = ax1.patches
            label1 = [f"label{i}" for i in range(len(rects))]
            for rect, label in zip(rects, label1):
                height = rect.get_height()
                ax1.text(rect.get_x() + rect.get_width() / 2, height + 5, '{:,}'.format(int(height)), size=10,weight='bold',ha="center", va="bottom")

            #Add average as plot
            meanval = df_temp['Expenses'].mean()
            ax1.axhline(meanval, color='darkred', linewidth=2,ls=  '--')
            ax1.text(rects[0].get_x(),meanval+5,'AVG EXPENSES: ${:,}'.format(int(meanval)),size=16,weight='bold',ha='left',va='bottom')
            ax1.axhline(df_temp['Income'].mean(), color='darkgreen', linewidth=2,ls=  '--')
            ax1.text(rects[0].get_x(),df_temp['Income'].mean()+5,'AVG INCOME: ${:,}'.format(int(df_temp['Income'].mean())),size=16,weight='bold',ha='left',va='bottom')

            ax1.set_ylabel('MONTHLY AMOUNT',size=18,weight='bold')
            ax1.set_xlabel('')
            ax1.legend(fontsize=17,loc = 'upper left')

            ax1.set_title('{} MONTHLY INCOME & EXPENSES'.format(year),size=25,weight='bold')
            ax1.set_yticks(np.arange(0,np.ceil(df_temp.max().max()/1000)*1000,1000))
            ax1.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
            ax1.tick_params(axis='y',labelsize=18)
            ax1.set_xticklabels(labels)
            ax1.tick_params(axis='x',labelsize=16)
            ax1.grid()

            #Heatmap plot
            df_heatmap=df_spending.loc[df_spending['YYYY']==year].groupby(['MM','Overall_Category'])['Amount'].sum().astype(int)*-1
            df_heatmap=df_heatmap.reset_index(name='total')
            df_heatmap=df_heatmap.pivot(index='Overall_Category', columns='MM', values='total')
            df_heatmap['AVG'] = np.round(df_heatmap.fillna(0).mean(axis=1),0)

            axheat = sns.heatmap(data=df_heatmap,
                              annot=True, 
                              cmap='rocket_r',
                              ax=ax2,fmt='g',
                              annot_kws={"size": 12},
                              vmin=0,vmax = 1500)
            
            # use matplotlib.colorbar.Colorbar object
            cbar = axheat.collections[0].colorbar
            cbar.ax.tick_params(labelsize=14)
            ax2.set_ylabel('')
            ax2.set_xlabel('')
            t = ax2.get_xticklabels()
            ax2.set_xticklabels([calendar.month_abbr[x] for x in df_heatmap.columns.to_list()[:-1]])
            labels = [item.get_text() for item in ax2.get_xticklabels()]
            labels[-1] = 'Avg'
            ax2.set_xticklabels(labels)
            ax2.tick_params(axis='both',labelsize=16)

            #Pie Chart
            if year == currentyear:
                df_pie = df_spending.loc[(df_spending['YYYY']==year) & (df_spending['MM'] == currentmonth-1)].groupby('Overall_Category')['Amount'].sum()*-1
                title = '{}'.format(calendar.month_abbr[currentmonth-1])
            else:
                df_pie = df_spending.loc[df_spending['YYYY']==year].groupby('Overall_Category')['Amount'].sum()*-1
                title = '{}'.format(year)
            test = df_pie.loc[df_pie/df_pie.sum()<0.03]
            df_pie.drop(test.index,inplace=True)
            df_pie['Other'] = test.sum()

            colors = sns.color_palette('pastel')[0:len(df_pie.index)]
            df_pie.plot.pie(colors=colors,
                            autopct='%.0f%%',
                            ax=ax3,
                            textprops={'fontsize': 16},
                            pctdistance=0.4, 
                            labeldistance=1.02,
                            wedgeprops={'linewidth': 2.0, 'edgecolor': 'white'})
            ax3.set_ylabel('')
            ax3.set_title(title,size=20,weight='bold',y=0.95)
            pdf.savefig()
            if figdir == '':
                plt.savefig(figdir + '{}_breakdown.png'.format(year))
            else:
                plt.savefig(figdir + '/{}_breakdown.png'.format(year))
            plt.close()

        #Add overall yearly expenses over time
        df_income = df.loc[df['Overall_Category']=='Income']
        fig,(ax1,ax2) = plt.subplots(2,1,figsize=(15,15))
        if yearly_exclude_category:
            df_temp = pd.concat([df_spending.groupby('YYYY').sum()['Amount'].rename('Expenses')*-1,
                                 df_spending.loc[~df_spending['Overall_Category'].isin([yearly_exclude_category])].groupby('YYYY').sum()['Amount'].rename('Expenses - No {}'.format(yearly_exclude_category))*-1,
                                 df_income.groupby('YYYY')['Amount'].sum().rename('Income')],axis=1)        
            axt = df_temp.plot.bar(ax=ax1,width=0.9,color=['salmon','aquamarine','springgreen'],edgecolor=['darkred','darkslategray','darkgreen'])
        else:
            df_temp = pd.concat([df_spending.groupby('YYYY').sum()['Amount'].rename('Expenses')*-1,
                                 df_income.groupby('YYYY')['Amount'].sum().rename('Income')],axis=1)
            axt = df_temp.plot.bar(ax=ax1,width=0.9,color=['salmon','springgreen'],edgecolor=['darkred','darkgreen'])
            
            
        # Make some labels.
        rects = axt.patches
        labels = [f"label{i}" for i in range(len(rects))]
        for rect, label in zip(rects, labels):
            height = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width() / 2, height + 5, '{:,}'.format(int(height)), size=8,weight='bold',ha="center", va="bottom")

        #Add average as plot
        meanval = df_temp['Expenses'].mean()
        ax1.axhline(meanval, color='darkred', linewidth=2,ls=  '--')
        ax1.text(rects[0].get_x(),meanval+5,'AVG EXPENSES: ${:,}'.format(int(meanval)),size=12,weight='bold',ha='left',va='bottom')
        ax1.axhline(df_temp['Income'].mean(), color='darkgreen', linewidth=2,ls=  '--')
        ax1.text(rects[0].get_x(),df_temp['Income'].mean()+5,'AVG INCOME: ${:,}'.format(int(df_temp['Income'].mean())),size=12,weight='bold',ha='left',va='bottom')
        #Add labels, etc
        ax1.set_ylabel('YEARLY AMOUNT',size=16,weight='bold')
        ax1.set_xlabel('')
        ax1.set_title('YEARLY INCOME & EXPENSES',size=20,weight='bold')
        ax1.set_yticks(np.arange(0,np.ceil(df_temp.max().max()/1000)*1000,10000))
        ax1.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
        ax1.tick_params(axis='both',labelsize=16)
        ax1.legend(fontsize=14,loc = 'upper left')
        ax1.grid()

        ###Add monthly expenses over time
        df_temp = pd.concat([df_spending.groupby(['YYYY','MM']).sum()['Amount'].rename('Expenses')*-1,
                             df_income.groupby(['YYYY','MM'])['Amount'].sum().rename('Income')],axis=1)

        #Get labels
        labels = []
        for idx,row in df_temp.iterrows():
            labels.append('{}-{}'.format(calendar.month_abbr[idx[1]],str(idx[0])[-2:]))

        axt= df_temp.plot.bar(ax=ax2,color=['salmon','springgreen'],edgecolor=['darkred','darkgreen'])
        rects = axt.patches
        #Add average as plot
        meanval = df_temp['Expenses'].mean()
        ax2.axhline(meanval, color='darkred', linewidth=2,ls=  '--')
        ax2.text(rects[0].get_x(),meanval+5,'AVG EXPENSES: ${:,}'.format(int(meanval)),weight='bold',ha='left',va='bottom')

        ax2.axhline(df_temp['Income'].mean(), color='darkgreen', linewidth=2,ls=  '--')
        ax2.text(rects[0].get_x(),df_temp['Income'].mean()+5,'AVG INCOME: ${:,}'.format(int(df_temp['Income'].mean())),weight='bold',ha='left',va='bottom')
        ax2.set_ylabel('MONTHLY AMOUNT',size=16,weight='bold')
        ax2.set_xlabel('')
        ax2.legend(fontsize=14,loc = 'upper left')

        ax2.set_title('MONTHLY INCOME & EXPENSES',size=20,weight='bold')
        ax2.set_yticks(np.arange(0,np.ceil(df_temp.max().max()/1000)*1000,1000))
        ax2.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
        ax2.tick_params(axis='y',labelsize=16)
        ax2.set_xticklabels(labels)
        ax2.tick_params(axis='x',labelsize=12)
        ax2.grid()
        if figdir == '':
            plt.savefig(figdir + 'HISTORICAL_INCOME_EXPENSES.png')
        else:
            plt.savefig(figdir + '/HISTORICAL_INCOME_EXPENSES.png')
        pdf.savefig()
        plt.close()
        
def process_mintcsv(df,transfer_dict_file = r'./data/transfer_dictionary.txt'):
    '''
    DESCRIPTION
    Processes mint dataframes to convert credit and debits.  Also creates "Overall Categoy" Column which groups similar
    categories as perscribed by the "transfer_dict_file" input
    
    INPUT
    df = pandas dataframe,  Processed dataframe of mint data using standard column types as designated by mint
    transfer_dict_file = dictionary, transfer dictionary which maps Categories column to Overall_Category column
    
    OUPUT
    Processed dataframe that includes Overall Category Column as perscribed by the transfer dictionary
    
    '''
    #add datetime
    df['YYYY'] = df.index.year
    df['MM'] = df.index.month
    df['DD'] = df.index.day
    #convert credit/debit
    if (df['Amount'].astype(str).str.contains('\$').any()) | (df['Amount'].astype(str).str.contains(',').any()):
        df['Amount'] = df['Amount'].astype(object)
        df['Amount'] = df['Amount'].str.replace(r"[a-zA-Z$,]",'')
        df['Amount'] = df['Amount'].astype(float)
    df.loc[df['Transaction Type']=='debit','Amount'] = df.loc[df['Transaction Type']=='debit','Amount'] * -1
    #load category mapper
    myfile = open(transfer_dict_file, 'r')
    transfer_dictionary = {}
    for line in myfile:
        k, v = line.strip().split(':')
        transfer_dictionary[k.strip()] = v.strip()        
    #Map Categories to overall category
    df['Overall_Category'] = df['Category'].map(transfer_dictionary)
    return df
#def process_yearly(df):