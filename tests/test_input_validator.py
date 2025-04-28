import pytest
from input.input_validator import generate_random_md5

def test_generate_random_md5_length():
    md5_hash = generate_random_md5(16)
    assert len(md5_hash) == 32, "MD5 hash length should be 32 characters"

def test_generate_random_md5_uniqueness():
    md5_hash1 = generate_random_md5(16)
    md5_hash2 = generate_random_md5(16)
    assert md5_hash1 != md5_hash2, "MD5 hashes should be unique for different random strings"

def test_generate_random_md5_default_length():
    md5_hash = generate_random_md5()
    assert len(md5_hash) == 32, "MD5 hash length should be 32 characters when using default length"

def test_generate_random_md5_different_data_lengths():
    md5_hash_8 = generate_random_md5(8)
    md5_hash_32 = generate_random_md5(32)
    assert len(md5_hash_8) == 32, "MD5 hash length should be 32 characters for 8 character input"
    assert len(md5_hash_32) == 32, "MD5 hash length should be 32 characters for 32 character input"