"use client";

// MOCK cart. In-memory only — state is lost on refresh and is NOT shared with a
// server. A real integration would POST to your commerce backend here. It exists
// so the add_to_cart client-side tool has something concrete to call.

export type CartLine = { productId: string; quantity: number };

const lines: CartLine[] = [];

export function addToCart(productId: string, quantity = 1): CartLine {
  const existing = lines.find((l) => l.productId === productId);
  if (existing) {
    existing.quantity += quantity;
    return existing;
  }
  const line: CartLine = { productId, quantity };
  lines.push(line);
  return line;
}

export function getCart(): CartLine[] {
  return lines.map((l) => ({ ...l }));
}
