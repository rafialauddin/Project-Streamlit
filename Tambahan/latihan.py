import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

# Membaca file CSV
orders_df = pd.read_csv('https://github.com/rafialauddin/Project-Streamlit/blob/main/E-Commerce%20Public%20Dataset/orders_dataset.csv')
order_items_df = pd.read_csv('https://github.com/rafialauddin/Project-Streamlit/blob/main/E-Commerce%20Public%20Dataset/order_items_dataset.csv')
products_df = pd.read_csv('https://github.com/rafialauddin/Project-Streamlit/blob/main/E-Commerce%20Public%20Dataset/products_dataset.csv')
products_name_df = pd.read_csv('https://github.com/rafialauddin/Project-Streamlit/blob/main/E-Commerce%20Public%20Dataset/products_dataset.csv')
products_name_english_df = pd.read_csv('https://github.com/rafialauddin/Project-Streamlit/blob/main/E-Commerce%20Public%20Dataset/product_category_name_translation.csv')

# Melakukan inner join antara orders_df dan products_df berdasarkan kolom 'product_id'
new_order_df = pd.merge(orders_df, 
                        order_items_df[["order_id", "order_item_id","product_id", "seller_id"]], 
                        on='order_id', 
                        how='inner')

order_with_products_name_df = pd.merge(new_order_df, 
                        products_df[["product_id", "product_category_name"]], 
                        on='product_id', 
                        how='inner')

order_with_products_name_english_df = pd.merge(order_with_products_name_df, 
                        products_name_english_df, 
                        on='product_category_name', 
                        how='inner')


# Menampilkan nama kolom di DataFrame hasil


duplikasi = order_with_products_name_english_df.duplicated().sum()

# Menampilkan baris yang merupakan duplikasi
print("Duplikasi:")
print(duplikasi)

# Menghapus Duplikasi

order_with_products_name_english_df = order_with_products_name_english_df.drop_duplicates()

# Menampilkan DataFrame setelah menghapus duplikasi
print("DataFrame tanpa duplikasi:")
print(order_with_products_name_english_df)

order_with_products_name_english_df = order_with_products_name_english_df.dropna(subset=['order_delivered_carrier_date'])
order_with_products_name_english_df = order_with_products_name_english_df.dropna(subset=['order_approved_at'])

print(order_with_products_name_english_df.isna().sum())

# Konversi Tanggal
order_with_products_name_english_df['order_approved_at'] = pd.to_datetime(order_with_products_name_english_df['order_approved_at'], format='%Y-%m-%d %H:%M:%S')

# Mengambil tahun minimum dan maksimum
tahun_minimum = order_with_products_name_english_df['order_approved_at'].min().year
tahun_maksimum = order_with_products_name_english_df['order_approved_at'].max().year

# EDA
print("\nPenjualan Product Terbanyak Sejak ", tahun_minimum," Sampai ", tahun_maksimum)
total_penjualan = order_with_products_name_english_df.groupby('product_category_name_english')['order_item_id'].sum().reset_index().sort_values(by='order_item_id', ascending=False)
print(total_penjualan)

# Mengambil Top 20 Items
top_20_items = total_penjualan.nlargest(20, 'order_item_id')
# Aliasing Nama Kolom
total_penjualan = total_penjualan.rename(columns={'order_item_id': 'Total_Sales'})
total_penjualan = total_penjualan.rename(columns={'product_category_name_english': 'Products_Name'})
top_20_items = top_20_items.rename(columns={'order_item_id': 'Total_Sales'})
top_20_items = top_20_items.rename(columns={'product_category_name_english': 'Products_Name'})
# Sorting
top_20_items = top_20_items.sort_values(by='Total_Sales', ascending=True)


st.set_page_config(
    page_title="Aplikasi Penjualan Produk",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Judul aplikasi
st.title("Visualisasi Data E-Commerce")

# Menampilkan DataFrame
st.write("Data Penjualan Produk Terbanyak:")
st.dataframe(total_penjualan)

# Visualisasi menggunakan Plotly

fig = px.bar(top_20_items, x='Total_Sales', y='Products_Name', title='Data 20 Product Terlaris')
fig.update_layout(
    xaxis_title='Total Penjualan',
    yaxis_title='Nama Produk',
    font=dict(family='Arial', size=10, color='black'),
    bargap=0.1,
    height=600,  
    width=800,   
)
fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=3, opacity=0.6, text=top_20_items['Total_Sales'])

st.plotly_chart(fig)

# Rentang waktu penjualan
st.write(f"Penjualan Product Terbanyak Sejak {tahun_minimum} Sampai {tahun_maksimum}")

# Analisis atau penjelasan tambahan tentang data penjualan
st.write("Dapat dilihat pada tabel diatas bahwa kategori product terlaris dalam situs ini adalah Bed Bath n Table. Dalam 2 tahun, kategori ini laku sebanyak 13.620 items. Selanjutnya kita dapat melihat product dekorasi dan furniture merupakan penyumbang market ke-2 dalam e-commerce ini dengan 11.398 items terjual. Berdasarkan visualisasi data yang dapat dilihat, kita dapat simpulkan bahwa E-Commerce ini sangat baik untuk membeli keperluan-keperluan rumah tangga seperti perabot, dan aksesoris lainnya.")


st.header("Trend Penjualan Per-Product")

# Membuat Filter Selectbox
produk_terpilih = st.selectbox('Pilih Produk:', order_with_products_name_english_df['product_category_name_english'].unique())
filtered_df = order_with_products_name_english_df[order_with_products_name_english_df['product_category_name_english'] == produk_terpilih]

# Konversi kolom datetime menjadi objek datetime Pandas
filtered_df['order_approved_at'] = pd.to_datetime(filtered_df['order_approved_at'], format='%Y-%m-%d %H:%M:%S')

# Mendapatkan timestamp hanya untuk tahun dan bulan
filtered_df['order_approved_at'] = filtered_df['order_approved_at'].apply(lambda x: x.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())

# Membuat DataFrame dengan total penjualan per produk dan bulan
total_penjualan_per_produk = filtered_df.groupby(['order_approved_at'])['order_item_id'].sum().reset_index()

# Urutkan DataFrame secara ascending berdasarkan tahun dan bulan
total_penjualan_per_produk = total_penjualan_per_produk.sort_values(by=['order_approved_at'], ascending=True)

# Konversi timestamp kembali menjadi format tanggal
total_penjualan_per_produk['order_approved_at'] = pd.to_datetime(total_penjualan_per_produk['order_approved_at'], unit='s')

# Plotly Line Chart
fig = px.line(total_penjualan_per_produk, x='order_approved_at', y='order_item_id',
              title=f'Tren Penjualan Produk {produk_terpilih} per Bulan',
              labels={'order_item_id': 'Total Penjualan', 'order_approved_at': 'Tanggal'})
fig.update_layout(
    xaxis_title='Tanggal',
    yaxis_title='Total Penjualan',
    font=dict(family='Arial', size=12, color='black'),
    height=600,  # Atur tinggi grafik
    width=800    # Atur lebar grafik
)

# Format sumbu x agar menampilkan bulan dan tanggal yang sesuai
fig.update_xaxes(
    tickformat="%Y-%m",
    tickmode="linear",
    tick0=total_penjualan_per_produk['order_approved_at'].min(),
    dtick='M1',
)

st.plotly_chart(fig)

st.write("Dari Trendline diatas dapat kita lihat hampir pada semua kategori cenderung positif trend nya, artinya E-Commerce ini cukup sukses dalam pengembangan citra mereka. Namun meski begitu terdapat kategori-kategori yang cenderung menurun memasuki Q3 pada Tahun 2018 ini, mereka tetap harus mengevaluasi apa yang terjadi. Namun secara Overall E-Commerce ini sudah berjalan dengan trend yang positif")

# Tautan ke sumber data
st.markdown("[Sumber Data](https://drive.google.com/drive/folders/18EYx4gz8U8SjR7lzY2HxJoN5aLnNWM_M)")


# Untuk Men-Download CSV
#order_with_products_name_english_df.to_csv('output_file.csv', index=False)
#total_penjualan.to_csv('total_penjualan.csv', index=False)

