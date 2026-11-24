from src.loader import load_survey

def test_rows_and_cols():
    df = load_survey()
    assert len(df) == 49_123          # nombre de répondants attendu
    assert len(df.columns) == 170