#!/usr/bin/env python3
"""Lightweight test to verify company query detection without loading embedding model."""

user_query = 'dimana letak perusahaannya'
company_keywords = ['letak', 'dimana', 'mana perusahaan', 'lokasi', 'alamat', 'jam operasional', 'jam kerja', 'operasional', 'kantor', 'office', 'perusahaan']

is_company_query = any(keyword in user_query.lower() for keyword in company_keywords)

print(f"Query: '{user_query}'")
print(f"Is company query: {is_company_query}")
print()

# Check which keywords matched
matched = [kw for kw in company_keywords if kw in user_query.lower()]
print(f"Matched keywords: {matched}")
