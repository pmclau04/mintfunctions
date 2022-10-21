'mintfunctions' is a Python wrapper for the postprocessing finance data from your [Mint](mint.com) account

<!-- Use -->
## Use
This set of functions makes postprocessing Mint personal finance data easy, and generates monthly reports for your spending.  

### Load Mint Transactions data as a dataFrame
First, download your spending data from [mint](mint.com).  Then, load the transaction data as a a dataframe and run 'process_mintcsv' to prep the dataframe for report generation.  For example:

'''python
#Load historical data
df = pd.read_csv(r'./data/transactions.csv',index_col='Date',encoding='latin-1',infer_datetime_format=True)
df.index = pd.to_datetime(df.index)
df = mintfunctions.process_mintcsv(df)

'''

### Generate report
Once the transaction data is pre-processed, you can run the 'mintfunctions.gerate_pdf' function to visualize your spending data and create a monthly report.  Required and optional inputs are as follows:

**Required**
df = dataframe of spending and income data
**Optional**
-  pdfdir = string, path to save monthly report pdf.  Default = '', 
- figdir = string, path to save figures.  Default = r'./figures',
- yearly_exclude_category = string, optional input that excludes a single category from your yearly spending amounts.  For example, user can specify 'Home Improvement' to exclude all home improvment expenses from plot.  Default = None
- spending_drop_categories = list of strings, overall categories to exclude from spending dataframe.  Default = ['Income', 'Transfer','Reimbursement','Credit Card Payment','Loans']

Example python input to generate report:
'''python
mintfunctions.generate_pdf(df,
pdfdir = '', 
figdir = r'./figures',
yearly_exclude_category = None, 
spending_drop_categories = ['Income', 'Transfer','Reimbursement','Credit Card Payment','Loans'])
'''
<p align="right">(<a href="#readme-top">back to top</a>)</p>
##Output
Code will output monthly report pdf, the following figures are an example of the yearly spending breakdown, and the categorical spending breakdown.  Example figures below for each, taken from dummy monthly report.

**Example Categorical plots generated in pdf**
![image](https://user-images.githubusercontent.com/27655508/197305919-a2a412e4-8a68-47d4-b1c4-1883c50cec85.png)

**Example Yearly & Monthly spending breakdown plots**
![image](https://user-images.githubusercontent.com/27655508/197305934-be8842c6-f821-42e6-bd60-68a13d9e04e3.png)

## Prerequisites to run mintfunctions
These are the required packages for using mintfunctions. 
* seaborn
* matplotlib
* calendar
* datetime
* pandas
* numpy
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/pmclau04/mintfunctions.git
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- PROJECT LINK -->
## Link to mintfunctions

Project Link: [https://github.com/pmclau04/mintfunctions](https://github.com/pmclau04/mintfunctions)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<p align="right">(<a href="#readme-top">back to top</a>)</p>
