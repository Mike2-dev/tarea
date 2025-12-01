from src.UNEZPANOL import evaluar

def test_evaluar_suma():
    assert evaluar("2 + 3") == 5

def test_evaluar_comparacion():
    assert evaluar("5 > 2") is True
