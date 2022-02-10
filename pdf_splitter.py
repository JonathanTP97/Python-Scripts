from PyPDF2 import PdfFileReader, PdfFileWriter


def split_pdf(pdf):
    with open(pdf, 'rb') as f:
        pdf = PdfFileReader(f)
        print(pdf.getNumPages())

        for i in range(9):
            print(type(i))
            number = int(i) + 1
            print(number)
            write_book(number, pdf)
        write_book_end(pdf)

        # with open(output, 'wb') as out:
            # pdf_writer.write(out)
        # for page in range()


def write_book(num, pdf):
    global count
    pdf_writer = PdfFileWriter()
    for page in range(37):
        print(page)
        pdf_writer.addPage(pdf.getPage(count))
        count = count + 1
    with open("out_" + str(num) + ".pdf", 'wb') as out:
        pdf_writer.write(out)


def write_book_end(pdf):
    global count
    pdf_writer = PdfFileWriter()
    for page in range(40):
        pdf_writer.addPage(pdf.getPage(count))
        count = count + 1
    with open("out_10.pdf", 'wb') as out:
        pdf_writer.write(out)


if __name__ == '__main__':
    count = 0
    split_pdf("file.pdf")  # 373 / 10 37 pages at a time
