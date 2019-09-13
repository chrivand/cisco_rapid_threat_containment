#!/usr/bin/python3
import os
import sys
import traceback

def a(y):
    x = y/0

def b(i):
    a(i)


try:
    b(65)
except Exception as e:
    t = traceback.format_exc()
    print(t)
