import { computed, ref, watch } from 'vue';
import { defineStore } from 'pinia';
import { api } from '@/services/api';

const CART_STORAGE_KEY = 'cirujano-shop-cart-v1';
const SHIPPING_STORAGE_KEY = 'cirujano-shop-shipping-v1';
const MAX_QTY_PER_PRODUCT = 20;

type ShippingOption = {
  key: string;
  name: string;
  price: number;
};

type CartItem = {
  id: number;
  qty: number;
  name: string;
  sku: string;
  price: number;
  image_url: string;
  family: string;
  category: string;
  description: string;
  stock_unit: string;
  available_stock: number;
  sellable_stock: number;
  min_stock: number;
  store_visible: boolean;
  enabled: boolean;
  is_low_stock: boolean;
  stock_alert_level: string | null;
  [key: string]: any;
};

type RawCartItem = Partial<CartItem> & {
  id?: number | string;
  product_id?: number | string;
  qty?: number | string;
  quantity?: number | string;
  unit_price?: number | string;
};

const SHIPPING_OPTIONS: ShippingOption[] = [
  { key: 'pickup', name: 'Retiro en taller', price: 0 },
  { key: 'manual', name: 'Despacho coordinado manualmente', price: 0 },
];

function normalizeQty(value: unknown): number {
  const qty = Number(value);
  if (!Number.isFinite(qty)) {
    return 0;
  }
  return Math.min(MAX_QTY_PER_PRODUCT, Math.max(0, Math.floor(qty)));
}

function normalizeCartItem(item: RawCartItem | null | undefined): CartItem | null {
  if (!item || typeof item !== 'object') {
    return null;
  }

  const id = Number(item.id || item.product_id || 0);
  const qty = normalizeQty(item.qty || item.quantity || 0);

  if (id <= 0 || qty <= 0) {
    return null;
  }

  return {
    id,
    qty,
    name: String(item.name || '').trim(),
    sku: String(item.sku || '').trim(),
    price: Number(item.price || item.unit_price || 0),
    image_url: String(item.image_url || '').trim(),
    family: String(item.family || '').trim(),
    category: String(item.category || '').trim(),
    description: item.description || '',
    stock_unit: String(item.stock_unit || 'u').trim() || 'u',
    available_stock: Number(item.available_stock || 0),
    sellable_stock: Number(item.sellable_stock || 0),
    min_stock: Number(item.min_stock || 0),
    store_visible: item.store_visible !== false,
    enabled: item.enabled !== false,
    is_low_stock: Boolean(item.is_low_stock),
    stock_alert_level: item.stock_alert_level || null,
  };
}

function maxAllowedQty(item: CartItem | null | undefined): number {
  const rawSellable = item?.sellable_stock;
  if (rawSellable !== undefined && rawSellable !== null && String(rawSellable).trim() !== '') {
    const sellable = Number(rawSellable);
    if (Number.isFinite(sellable) && sellable > 0) {
      return Math.min(MAX_QTY_PER_PRODUCT, sellable);
    }
  }
  return MAX_QTY_PER_PRODUCT;
}

function persistJson(key: string, value: unknown): void {
  if (typeof window === 'undefined') {
    return;
  }
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // noop
  }
}

export const useShopCartStore = defineStore('shop-cart', () => {
  const items = ref<CartItem[]>([]);
  const selectedShippingKey = ref<string>(SHIPPING_OPTIONS[0].key);
  const hydrated = ref(false);
  const submitting = ref(false);

  const shippingOptions = SHIPPING_OPTIONS;

  const currentShipping = computed<ShippingOption>(() => {
    return shippingOptions.find((option) => option.key === selectedShippingKey.value) || shippingOptions[0];
  });

  const itemsCount = computed<number>(() => items.value.reduce((sum, item) => sum + normalizeQty(item.qty), 0));

  const totals = computed(() => {
    const productsSubtotal = items.value.reduce((sum, item) => sum + (Number(item.price || 0) * normalizeQty(item.qty)), 0);
    const hasQuotedAmount = items.value.some((item) => Number(item.price || 0) > 0);
    const shippingPrice = Number(currentShipping.value.price || 0);

    return {
      itemsCount: itemsCount.value,
      productsSubtotal,
      shippingPrice,
      grandTotal: productsSubtotal + shippingPrice,
      hasQuotedAmount,
    };
  });

  function hydrate(): void {
    if (hydrated.value || typeof window === 'undefined') {
      return;
    }

    try {
      const raw = window.localStorage.getItem(CART_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          items.value = parsed.map((entry) => normalizeCartItem(entry)).filter((entry): entry is CartItem => entry !== null);
        } else if (parsed && typeof parsed === 'object') {
          items.value = Object.entries(parsed)
            .map(([id, qty]) => normalizeCartItem({ id, qty }))
            .filter((entry): entry is CartItem => entry !== null);
        }
      }
    } catch {
      items.value = [];
    }

    try {
      const rawShipping = window.localStorage.getItem(SHIPPING_STORAGE_KEY);
      if (rawShipping) {
        const parsedShipping = String(JSON.parse(rawShipping) || '');
        if (shippingOptions.some((option) => option.key === parsedShipping)) {
          selectedShippingKey.value = parsedShipping;
        }
      }
    } catch {
      selectedShippingKey.value = shippingOptions[0].key;
    }

    hydrated.value = true;
  }

  function setShippingKey(key: unknown): void {
    const nextKey = String(key || '');
    if (shippingOptions.some((option) => option.key === nextKey)) {
      selectedShippingKey.value = nextKey;
    }
  }

  function replaceItems(nextItems: unknown[]): void {
    items.value = (Array.isArray(nextItems) ? nextItems : [])
      .map((entry) => normalizeCartItem(entry as RawCartItem))
      .filter((entry): entry is CartItem => entry !== null);
  }

  function syncCatalog(products: unknown[]): void {
    const catalog = new Map<string, CartItem>(
      (Array.isArray(products) ? products : [])
        .map((product) => normalizeCartItem({ ...(product as RawCartItem), qty: 1 }))
        .filter((product): product is CartItem => product !== null)
        .map((product) => [String(product.id), product])
    );

    if (!catalog.size) {
      items.value = [];
      return;
    }

    items.value = items.value
      .map((item) => {
        const product = catalog.get(String(item.id));
        if (!product || !product.store_visible || product.enabled === false) {
          return null;
        }
        const limit = maxAllowedQty(product);
        const qty = Math.min(normalizeQty(item.qty), limit);
        if (qty <= 0) {
          return null;
        }
        return normalizeCartItem({ ...product, qty });
      })
      .filter((entry): entry is CartItem => entry !== null);
  }

  function canAddProduct(product: unknown): boolean {
    const normalized = normalizeCartItem({ ...(product as RawCartItem), qty: 1 });
    if (!normalized || normalized.store_visible === false || normalized.enabled === false) {
      return false;
    }
    const current = items.value.find((entry) => String(entry.id) === String(normalized.id));
    const currentQty = normalizeQty(current?.qty || 0);
    return currentQty < maxAllowedQty(normalized);
  }

  function addProduct(product: unknown): boolean {
    const normalized = normalizeCartItem({ ...(product as RawCartItem), qty: 1 });
    if (!normalized) {
      return false;
    }

    const currentIndex = items.value.findIndex((entry) => String(entry.id) === String(normalized.id));
    if (currentIndex < 0) {
      if (!canAddProduct(normalized)) {
        return false;
      }
      items.value = [...items.value, normalized];
      return true;
    }

    const current = items.value[currentIndex];
    const nextQty = Math.min(normalizeQty(current.qty + 1), maxAllowedQty(normalized));
    if (nextQty <= normalizeQty(current.qty)) {
      return false;
    }

    const nextItems = [...items.value];
    const nextItem = normalizeCartItem({ ...current, ...normalized, qty: nextQty });
    if (!nextItem) {
      return false;
    }
    nextItems[currentIndex] = nextItem;
    items.value = nextItems;
    return true;
  }

  function removeItem(productId: unknown): void {
    items.value = items.value.filter((entry) => String(entry.id) !== String(productId));
  }

  function changeQty(productId: unknown, delta: unknown): void {
    const index = items.value.findIndex((entry) => String(entry.id) === String(productId));
    if (index < 0) {
      return;
    }

    const current = items.value[index];
    const nextQty = Math.min(
      maxAllowedQty(current),
      normalizeQty(Number(current.qty || 0) + Number(delta || 0))
    );

    if (nextQty <= 0) {
      removeItem(productId);
      return;
    }

    const nextItems = [...items.value];
    const nextItem = normalizeCartItem({ ...current, qty: nextQty });
    if (!nextItem) {
      return;
    }
    nextItems[index] = nextItem;
    items.value = nextItems;
  }

  function clear(): void {
    items.value = [];
  }

  function buildRequestPayload(notes = ''): Record<string, any> {
    return {
      shipping_key: currentShipping.value.key,
      shipping_label: currentShipping.value.name,
      shipping_price: Number(currentShipping.value.price || 0),
      notes: String(notes || '').trim() || null,
      items: items.value.map((item) => ({
        product_id: item.id,
        sku: item.sku,
        name: item.name,
        quantity: normalizeQty(item.qty),
        unit_price: Number(item.price || 0),
      })),
    };
  }

  async function submitRequest(notes = ''): Promise<Record<string, any> | null> {
    if (!items.value.length) {
      throw new Error('El carrito está vacío');
    }

    submitting.value = true;
    try {
      const response = await api.post('/client/store/purchase-requests', buildRequestPayload(notes));
      const request = response?.data?.request || null;
      clear();
      return request;
    } finally {
      submitting.value = false;
    }
  }

  watch(items, (value) => {
    persistJson(CART_STORAGE_KEY, value);
  }, { deep: true });

  watch(selectedShippingKey, (value) => {
    persistJson(SHIPPING_STORAGE_KEY, value);
  });

  return {
    items,
    hydrated,
    submitting,
    shippingOptions,
    selectedShippingKey,
    currentShipping,
    itemsCount,
    totals,
    hydrate,
    setShippingKey,
    replaceItems,
    syncCatalog,
    canAddProduct,
    addProduct,
    removeItem,
    changeQty,
    clear,
    buildRequestPayload,
    submitRequest,
  };
});
