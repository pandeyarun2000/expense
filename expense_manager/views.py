import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .models import Expense
from fuzzywuzzy import process, fuzz
from django.http import HttpResponse

def upload_dataset(request):
    if request.method == 'POST':
        dataset_file = request.FILES['dataset']
        with open('dataset.csv', 'wb') as file:
            for chunk in dataset_file.chunks():
                file.write(chunk)
        return render(request, 'expense_manager/upload_expense_data.html')
    return render(request, 'expense_manager/upload_dataset.html')

def all_expenses(request):
    all_expenses = pd.read_csv('expense_data.csv')

    # Read the dataset CSV file to get category information
    dataset = pd.read_csv('dataset.csv')
    merchant_names = dataset['Merchant Name'].values
    expense_categories = dataset['Expense Category'].values

    # Function to categorize an expense based on the merchant's name
    def categorize_expense(merchant_name):
        closest_match = process.extractOne(merchant_name, merchant_names, scorer=fuzz.ratio)
        if closest_match:
            closest_match_name = closest_match[0]
            closest_match_index = dataset[dataset['Merchant Name'] == closest_match_name].index[0]
            return expense_categories[closest_match_index]
        else:
            return 'Other'

    # Add a new 'Category' column for expense categories
    all_expenses['Category'] = all_expenses['Merchant'].apply(categorize_expense)

    return render(request, 'expense_manager/all_expenses.html', {
        'all_expenses': all_expenses,
    })

def categorize_expense(request):
    if request.method == 'POST':
        expense_data_files = request.FILES.getlist('expense_data')

        all_expenses = pd.DataFrame()

        for expense_data_file in expense_data_files:
            with open('expense_data.csv', 'wb') as file:
                for chunk in expense_data_file.chunks():
                    file.write(chunk)
            expense_data = pd.read_csv('expense_data.csv')
            all_expenses = pd.concat([all_expenses, expense_data])

        dataset = pd.read_csv('dataset.csv')
        merchant_names = dataset['Merchant Name'].values
        expense_categories = dataset['Expense Category'].values

        def categorize_expense(merchant_name):
            closest_match = process.extractOne(merchant_name, merchant_names, scorer=fuzz.ratio)
            if closest_match:
                closest_match_name = closest_match[0]
                closest_match_index = dataset[dataset['Merchant Name'] == closest_match_name].index[0]
                return expense_categories[closest_match_index]
            else:
                return 'Other'

        all_expenses['Category'] = all_expenses['Merchant'].apply(categorize_expense)

        for index, row in all_expenses.iterrows():
            try:
                expense = Expense.objects.get(merchant=row['Merchant'])
                expense.category = row['Category']
                expense.save()
            except Expense.DoesNotExist:
                pass  # Handle if the expense does not exist in the database

        category_expenses = all_expenses.groupby('Category')['Debit'].sum() - all_expenses.groupby('Category')['Credit'].apply(lambda x: x.abs().sum())

        plt.figure(figsize=(10, 6))
        category_expenses.plot(kind='bar', color='steelblue')
        plt.xlabel('Expense Category')
        plt.ylabel('Total Expense')
        plt.title('Expense Breakdown by Category')
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()

        categorized_expenses = category_expenses.reset_index().values.tolist()

        return render(request, 'expense_manager/categorized_expenses.html', {
            'categorized_expenses': categorized_expenses,
            'image_base64': image_base64,
        })

    return render(request, 'expense_manager/upload_expense_data.html')

from django.http import HttpResponse
import pandas as pd

def download_csv(request):
    all_expenses = pd.read_csv('expense_data.csv')  # Read the expense data CSV

    # Read the dataset CSV file to get category information
    dataset = pd.read_csv('dataset.csv')
    merchant_names = dataset['Merchant Name'].values
    expense_categories = dataset['Expense Category'].values

    # Function to categorize an expense based on the merchant's name
    def categorize_expense(merchant_name):
        closest_match = process.extractOne(merchant_name, merchant_names, scorer=fuzz.ratio)
        if closest_match:
            closest_match_name = closest_match[0]
            closest_match_index = dataset[dataset['Merchant Name'] == closest_match_name].index[0]
            return expense_categories[closest_match_index]
        else:
            return 'Other'

    # Add a new 'Category' column for expense categories
    all_expenses['Category'] = all_expenses['Merchant'].apply(categorize_expense)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_expenses.csv"'

    # Convert the DataFrame to CSV and write to the response
    all_expenses.to_csv(path_or_buf=response, index=False)

    return response

















