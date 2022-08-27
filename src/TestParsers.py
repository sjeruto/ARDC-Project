from diary_parsers.NswParser import MinisterialDiaryParser, MinisterialDiaryEntry

def extract_pdf_data(folder, jurisdiction):
    parser = MinisterialDiaryParser(folder, jurisdiction)
    data = parser.extract_data()
    if len(parser.errors) > 0:
        with open('ministerial_diary_errors.log', 'a') as f:
            f.writelines(parser.errors)

extract_pdf_data('NSW_pdfs', 'NSW')
extract_pdf_data('QLD_pdfs', 'QLD_pdfs')
