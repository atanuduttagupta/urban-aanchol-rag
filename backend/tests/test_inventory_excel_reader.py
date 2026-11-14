
import openpyxl

from backend.app.catalogue.excel_reader import read_products


def test_reader_skips_prefilled_id_only_rows_and_keeps_incomplete_products(
    tmp_path,
):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Products"

    worksheet.append(["Product Catalogue"])
    worksheet.append(
        ["product_id", "product_name", "category", "stock_quantity"]
    )

    worksheet.append(["UA-0001", "Test Saree", "Saree", 10])
    worksheet.append(["UA-0002", None, None, None])
    worksheet.append(["UA-0003", None, None, 5])

    file_path = tmp_path / "test_catalogue.xlsx"
    workbook.save(file_path)
    workbook.close()

    headers, products = read_products(str(file_path))

    assert len(products) == 2
    assert products[0]["product_id"] == "UA-0001"
    assert products[1]["product_id"] == "UA-0003"
    assert products[1]["stock_quantity"] == 5
