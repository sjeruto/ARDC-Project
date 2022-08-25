from diary_parsers.NswParser import NswParser, NswMinisterialDiaryEntry

def test_nsw_perser():
    parser = NswParser('NSW_pdfs')
    data = parser.extract_data()
    for error in parser.errors:
        print(error)

test_nsw_perser()