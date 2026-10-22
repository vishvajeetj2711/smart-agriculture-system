import json
from app import app
from modules.smart_irrigation import (
    calculate_irrigation_recommendation,
    get_crop_irrigation_rule,
    load_irrigation_rules,
    load_crop_water_requirements,
)

print('=== 1. TESTING ALL 5 VIVA TEST SCENARIOS ===')
# Test 1 — High Water Stress
t1 = calculate_irrigation_recommendation(crop='Cotton', soil_moisture=20, rain_prob=10, expected_rainfall=0)
assert t1['status'] == 'HIGH', f"Expected HIGH, got {t1['status']}"
assert t1['irrigation_required'] == True, 'Expected irrigation_required=True'
assert t1['water_stress'] == 'High'
print('  [PASS] Test 1: Cotton (20% moisture, 10% rain) -> HIGH stress, Irrigation Required')

# Test 2 — Normal Moisture
t2 = calculate_irrigation_recommendation(crop='Cotton', soil_moisture=55, rain_prob=20, expected_rainfall=0)
assert t2['status'] == 'LOW', f"Expected LOW, got {t2['status']}"
assert t2['irrigation_required'] == False, 'Expected irrigation_required=False'
assert t2['water_stress'] == 'Low'
print('  [PASS] Test 2: Cotton (55% moisture, 20% rain) -> LOW stress, No Irrigation Needed')

# Test 3 — Heavy Rain Expected
t3 = calculate_irrigation_recommendation(crop='Cotton', soil_moisture=30, rain_prob=85, expected_rainfall=15.0)
assert t3['status'] == 'WAIT', f"Expected WAIT, got {t3['status']}"
assert t3['irrigation_required'] == False, 'Expected irrigation_required=False'
assert 'Rain Delay' in t3['water_stress']
print('  [PASS] Test 3: Cotton (30% moisture, 85% rain, 15mm) -> WAIT, Delay Irrigation')

# Test 4 — Excessive Moisture
t4 = calculate_irrigation_recommendation(crop='Cotton', soil_moisture=85, rain_prob=0, expected_rainfall=0)
assert t4['status'] == 'NO_IRRIGATION', f"Expected NO_IRRIGATION, got {t4['status']}"
assert t4['irrigation_required'] == False, 'Expected irrigation_required=False'
print('  [PASS] Test 4: Cotton (85% moisture) -> NO_IRRIGATION, Saturated')

# Test 5 — Different Crop (Wheat)
t5 = calculate_irrigation_recommendation(crop='Wheat', soil_moisture=22, rain_prob=10, expected_rainfall=0)
assert t5['crop'] == 'Wheat'
assert t5['status'] == 'HIGH'
assert t5['irrigation_required'] == True
print('  [PASS] Test 5: Wheat (22% moisture) -> Loaded Wheat Rules, HIGH stress')


print('\n=== 2. TESTING ALL GUJARAT CROPS IN IRRIGATION.JSON ===')
rules = load_irrigation_rules()
req_crops = ['Cotton', 'Groundnut', 'Wheat', 'Bajra', 'Maize', 'Castor', 'Cumin', 'Mustard', 'Paddy', 'Sesame', 'Chickpea', 'Tomato', 'Onion']
for c in req_crops:
    rule = get_crop_irrigation_rule(c)
    assert rule['crop'] == c or rule.get('crop') == c, f'Missing rule for {c}'
    assert 'minimumMoisture' in rule
    assert 'idealMoistureMin' in rule
    assert 'idealMoistureMax' in rule
    assert 'criticalMoisture' in rule
    assert 'baseWaterPerAcre' in rule
    print(f"  [PASS] Crop {c}: Min={rule['minimumMoisture']}%, Ideal=[{rule['idealMoistureMin']}-{rule['idealMoistureMax']}], Base={rule['baseWaterPerAcre']} L/Ac")


print('\n=== 3. TESTING FLASK ROUTES & APIS ===')
client = app.test_client()

# Check Home page
res = client.get('/')
assert res.status_code == 200
assert b'Smart Irrigation' in res.data
print('  [PASS] GET / (Dashboard contains Smart Irrigation)')

# Check /crop page
res = client.get('/crop')
assert res.status_code == 200
print('  [PASS] GET /crop (Crop Recommendation intact)')

# Check /disease page
res = client.get('/disease')
assert res.status_code == 200
print('  [PASS] GET /disease (Disease Detection intact)')

# Check /weather page
res = client.get('/weather')
assert res.status_code == 200
print('  [PASS] GET /weather (Weather Forecast intact)')

# Check /market page
res = client.get('/market')
assert res.status_code == 200
print('  [PASS] GET /market (Market Prices intact)')

# Check /irrigation page GET
res = client.get('/irrigation')
assert res.status_code == 200
assert b'Smart Irrigation' in res.data
assert b'Cotton' in res.data
print('  [PASS] GET /irrigation (Irrigation page renders successfully)')

# Check /irrigation page POST
post_data = {
    'crop': 'Cotton',
    'growth_stage': 'Flowering',
    'land_area': '2.5',
    'soil_type': 'Black',
    'soil_moisture': '20',
    'soil_ph': '7.2',
    'irrigation_method': 'Drip',
    'water_availability': 'Medium',
    'city': 'Rajkot',
    'weather_temp': '33',
    'weather_humidity': '50',
    'rain_prob': '10',
    'expected_rainfall': '0'
}
res = client.post('/irrigation', data=post_data)
assert res.status_code == 200
assert b'HIGH WATER STRESS' in res.data or b'status-HIGH' in res.data
print('  [PASS] POST /irrigation (Form submission calculates and displays result)')

# Check AJAX API: /api/irrigation/calculate
res = client.post('/api/irrigation/calculate', json=post_data)
assert res.status_code == 200
json_data = res.get_json()
assert json_data['success'] == True
assert json_data['status'] == 'HIGH'
assert json_data['estimated_water_L'] > 0
print(f"  [PASS] POST /api/irrigation/calculate (JSON API returned {json_data['estimated_water_formatted']})")

# Check AJAX API: /api/irrigation/crop-rules/Groundnut
res = client.get('/api/irrigation/crop-rules/Groundnut')
assert res.status_code == 200
assert res.get_json()['rule']['crop'] == 'Groundnut'
print('  [PASS] GET /api/irrigation/crop-rules/Groundnut')

# Check AJAX API: /api/irrigation/crops
res = client.get('/api/irrigation/crops')
assert res.status_code == 200
assert len(res.get_json()['crops']) >= 13
print(f"  [PASS] GET /api/irrigation/crops (Returned {len(res.get_json()['crops'])} crops)")

# Check AJAX API: /api/irrigation/history
res = client.get('/api/irrigation/history')
assert res.status_code == 200
print(f"  [PASS] GET /api/irrigation/history (Returned {len(res.get_json()['history'])} entries)")

# Check AJAX API: /api/irrigation/send-alert
res = client.post('/api/irrigation/send-alert', json={'whatsapp_number': '9876543210', 'alert_text': 'Test Irrigation Alert'})
assert res.status_code == 200
assert res.get_json()['success'] == True
print('  [PASS] POST /api/irrigation/send-alert')

print('\n======================================================')
print('  ALL TESTS & VALIDATIONS COMPLETED WITH 100% SUCCESS!')
print('======================================================')
