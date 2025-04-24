magic_numbers = [
    4353685013742027030,
    1589775118099679493,
    366495898907640065,
    1460932163746533386,
    3638358163634682436,
]

ciphertext = bytearray()
for q in magic_numbers:
    ciphertext.extend(q.to_bytes(8, byteorder='little'))

result = bytearray((b ^ 90) + 21 for b in ciphertext)

print(''.join(chr(b) for b in result))
