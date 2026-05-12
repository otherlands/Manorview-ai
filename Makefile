run:
	uvicorn gateway.main:app --host 0.0.0.0 --port 9000

index:
	python scripts/build_index.py

anchor:
	python scripts/daily_anchor.py
