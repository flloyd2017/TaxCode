
import streamlit as st
import plotly.graph_objects as go

st.title('Tax Sankey Diagram Generator')

# Step 1: Income Sources
st.header('1. Enter Your Income Sources')

num_sources = st.number_input('How many income sources do you have?', min_value=1, max_value=10, value=1)

income_sources = []
for i in range(int(num_sources)):
    col1, col2 = st.columns(2)
    with col1:
        source_name = st.text_input(f'Income Source {i+1} Name', key=f'source_name_{i}')
    with col2:
        source_amount = st.number_input(f'Amount for {source_name}', min_value=0.0, step=1000.0, key=f'source_amount_{i}')
    income_sources.append({'name': source_name, 'amount': source_amount})

# Step 2: Deductions
st.header('2. Enter Your Deductions')

deductions = st.number_input('Total Deductions', min_value=0.0, step=1000.0)

# Example tax brackets (This is Joint from 2023)
tax_brackets = [
    {'limit': 22000, 'rate': 0.10},
    {'limit': 89450, 'rate': 0.12},
    {'limit': 190750, 'rate': 0.22},
    {'limit': 364200, 'rate': 0.24},
    {'limit': 462500, 'rate': 0.32},
    {'limit': 693750, 'rate': 0.35},
    {'limit': float('inf'), 'rate': 0.37},
]

# Calculations
total_income = sum([source['amount'] for source in income_sources])
taxable_income = max(0, total_income - deductions)

def calculate_taxes(income, brackets):
    taxes = []
    taxable_income = income
    previous_limit = 0
    total_tax = 0

    for bracket in brackets:
        if taxable_income > 0:
            income_in_bracket = min(bracket['limit'] - previous_limit, taxable_income)
            tax = income_in_bracket * bracket['rate']
            taxes.append({
                'bracket': f"{int(previous_limit)}-{int(bracket['limit'])}",
                'rate': bracket['rate'],
                'income': income_in_bracket,
                'tax': tax
            })
            total_tax += tax
            taxable_income -= income_in_bracket
            previous_limit = bracket['limit']
        else:
            break

    return taxes, total_tax

taxes_paid, total_tax = calculate_taxes(taxable_income, tax_brackets)
amount_kept = total_income - total_tax

# Prepare Sankey Diagram Data
labels = ['Income', 'Deductions', 'Taxable Income']
for tax in taxes_paid:
    labels.append(f"Bracket {tax['bracket']} ({int(tax['rate']*100)}%)")
labels.extend(['Total Tax Paid', 'Amount Kept'])

label_indices = {label: idx for idx, label in enumerate(labels)}

sources = []
targets = []
values = []

# First, link Income to Deductions (Deductions should be at the top)
sources.append(label_indices['Income'])
targets.append(label_indices['Deductions'])  # Deductions at the top
values.append(deductions)

# Then, link Income to Taxable Income
sources.append(label_indices['Income'])
targets.append(label_indices['Taxable Income'])
values.append(total_income - deductions)

# From Deductions to Amount Kept (since deductions are "kept")
sources.append(label_indices['Deductions'])
targets.append(label_indices['Amount Kept'])
values.append(deductions)

# From Taxable Income to Tax Brackets (income in each bracket)
for tax in taxes_paid:
    sources.append(label_indices['Taxable Income'])
    targets.append(label_indices[f"Bracket {tax['bracket']} ({int(tax['rate']*100)}%)"])
    values.append(tax['income'])

# From Tax Brackets to Total Tax Paid (tax in each bracket)
for tax in taxes_paid:
    sources.append(label_indices[f"Bracket {tax['bracket']} ({int(tax['rate']*100)}%)"])
    targets.append(label_indices['Total Tax Paid'])
    values.append(tax['tax'])

# From Tax Brackets to Amount Kept (income after tax in each bracket)
for tax in taxes_paid:
    income_after_tax = tax['income'] - tax['tax']
    sources.append(label_indices[f"Bracket {tax['bracket']} ({int(tax['rate']*100)}%)"])
    targets.append(label_indices['Amount Kept'])
    values.append(income_after_tax)

# Create the figure
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color='black', width=0.5),
        label=labels,
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
    ))])

fig.update_layout(title_text='Tax Flow Sankey Diagram', font_size=12)

# Display in Streamlit
st.header('3. Sankey Diagram')

st.plotly_chart(fig, use_container_width=True)

st.header('4. Summary')

st.write(f"**Total Income:** ${total_income:,.2f}")
st.write(f"**Deductions:** ${deductions:,.2f}")
st.write(f"**Taxable Income:** ${taxable_income:,.2f}")
st.write(f"**Total Tax Paid:** ${total_tax:,.2f}")
st.write(f"**Amount Kept:** ${amount_kept:,.2f}")
