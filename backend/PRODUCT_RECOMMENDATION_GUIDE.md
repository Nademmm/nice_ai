"""
PRODUCT RECOMMENDATION SYSTEM - HOW IT WORKS

=== FLOW DIAGRAM ===

User Query: "Saya butuh lampu untuk taman rumah"
    ↓
1. INTENT DETECTION
   - Detect keywords: "butuh", "lampu", "taman"
   - Intent = "product_recommendation" ✓
    ↓
2. DOCUMENT RETRIEVAL
   - Search vector store dengan query
   - Retrieve 15 most relevant documents
    ↓
3. INTELLIGENT CLASSIFICATION
   - Check if uploaded_knowledge contains product keywords
   - Keywords: watt, baterai, panel surya, spesifikasi, etc
   - If match → Set type = "product"
    ↓
4. DOCUMENT RANKING
   - Rank by: intent type matching + distance
   - Priority: uploaded docs > default docs
    ↓
5. USER NEED EXTRACTION
   - Extract location type: "taman" → ["taman"]
   - Extract scale: "rumah" → small/medium
   - Extract keywords for matching
    ↓
6. PRODUCT MATCHING
   - For each product, extract specs:
     • Watt: 40W, 60W, 80W, 100W, 120W
     • Battery: 20Ah, 40Ah, 50Ah, 80Ah
     • Suitable_for: taman, jalan, area, parkiran, dst
     • Lighting_duration: 6-8 jam, 10-12 jam, etc
   
   - Calculate match score (0-100):
     • Distance score (40 pts) - vector similarity
     • Scale matching (30 pts) - watt match dengan user scale
     • Location matching (30 pts) - suitable_for overlap
    ↓
7. RANKING & SELECTION
   - Sort products by match score (highest first)
   - Return top 2 recommendations with reasoning
    ↓
8. RESPONSE GENERATION
   Example:
   ✨ Berdasarkan kebutuhan Anda, berikut rekomendasi PJUTS:
   
   **1. Rekomendasi #1 - 40W (Match Score: 92%)**
   Produk: PJUTS 40W
   Spesifikasi: [extracted dari PDF]
   💡 Alasan: cocok untuk area taman, efisien untuk area terbatas


=== KEY IMPROVEMENTS ===

1. PRODUCT SPECS EXTRACTION
   - Auto-extract watt, battery, height, suitable_for dari content
   - Use regex untuk parse technical specs
   - Example: "PJUTS 60W dengan 40Ah LiFePO4" → watt=60, battery=40

2. USER NEED EXTRACTION  
   - Detect location type: taman, jalan, area, industri, parkiran, dsb
   - Detect scale: small (40-60W), medium (60-80W), large (100-120W)
   - Extract keywords untuk semantic matching

3. INTELLIGENT SCORING
   - Multi-factor scoring algorithm
   - Distance score: 0-40 pts (from vector search)
   - Scale matching: 0-30 pts (watt yang cocok)
   - Location matching: 0-30 pts (product suitable_for sesuai user location)
   - Total: 0-100 pts

4. PDF PRIORITY
   - Uploaded knowledge (PDF) SELALU diprioritaskan
   - Product detection otomatis di uploaded docs
   - Default products hanya sebagai fallback

5. BETTER INTENT DETECTION
   - Added keywords: taman, pencahayaan, penerangan, area, besar, kecil, luas
   - Better detection untuk kebutuhan spesifik
   - Threshold lowered untuk query pendek


=== EXAMPLE QUERIES & EXPECTED RESULTS ===

Q1: "Saya butuh lampu untuk taman rumah saya"
Expected: 
- Intent: product_recommendation
- User needs: location=taman, scale=small
- Top match: PJUTS 40W atau 60W
- Reason: cocok untuk taman, efisien untuk area terbatas

Q2: "Rekomendasi produk untuk area komersial yang luas"
Expected:
- Intent: product_recommendation
- User needs: location=komersial, scale=large
- Top match: PJUTS 100W atau 120W
- Reason: power tinggi untuk area luas, brightness maksimal

Q3: "Apa spesifikasi produk PJUTS?"
Expected:
- Intent: general atau product_recommendation
- Return: semua product specs dari PDF
- Show: watt, battery, suitable area, lighting duration


=== TESTING ===

Run test script:
    python test_product_recommendation.py

Check logs untuk:
- ✓ Intent detected correctly
- ✓ Documents retrieved dan ranked
- ✓ User needs extracted
- ✓ Products matched dengan score
- ✓ Response generated dengan reasoning


=== FILES MODIFIED ===

1. app/services/response_builder.py
   ✓ Added extract_product_specs()
   ✓ Added extract_user_needs()  
   ✓ Added calculate_product_match_score()
   ✓ Improved build_product_recommendation()

2. app/services/rag_service.py
   ✓ Added intelligent product classification di process_message()
   ✓ Increased n_results untuk product_recommendation (15 instead of 10)
   ✓ Added product keywords untuk classification
   ✓ Updated INTENT_KEYWORDS dengan lebih banyak keywords

3. test_product_recommendation.py
   ✓ New test script untuk validate recommendation


=== TROUBLESHOOTING ===

Problem: Rekomendasi tidak sesuai dengan tanya
Solution:
1. Check PDF content ada product specs lengkap
2. Pastikan keywords di PDF cocok (watt, battery, area)
3. Test dengan query lebih detail (e.g. "taman besar" bukan "taman")
4. Clear cache: del chroma_db folder → reload PDF

Problem: Product tidak ter-detect dari PDF
Solution:
1. Check upload.py - pastikan PDF diparse dengan benar
2. Verify PDF content dengan /documents endpoint
3. Add product keywords ke list jika ada new keywords di PDF

Problem: Wrong ranking/prioritization
Solution:
1. Check vector_store search - distance score
2. Verify intent detection - correct intent?
3. Check similarity threshold (sekarang 1.5)
4. Increase n_results jika perlu lebih banyak docs
"""