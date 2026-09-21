"""Assignment 2 helpers: demosaic, align/denoise, white balance."""

import numpy as np


def _to_float(img):
    x = np.asarray(img)
    if x.ndim == 3 and x.shape[2] > 1:
        x = x[..., 0]
    x = x.astype(np.float32)
    if x.max() > 1.5:
        x = x / 255.0
    return x


def interpolate_green(raw_img, offset_value):
    """offset_value=0: top-left is green. offset_value=1: its right neighbor is green."""
    raw = _to_float(raw_img)
    h, w = raw.shape
    rr, cc = np.indices((h, w))
    is_green = (rr + cc) % 2 == offset_value
    neigh = (
        np.roll(raw, 1, 0) + np.roll(raw, -1, 0) + np.roll(raw, 1, 1) + np.roll(raw, -1, 1)
    ) / 4.0
    green = np.where(is_green, raw, neigh)
    return green[2:-2, 2:-2]


def interpolate_redblue(raw_img, offset_pair):
    """offset_pair=(row0, col0) of the first sample of this channel."""
    raw = _to_float(raw_img)
    h, w = raw.shape
    ro, co = offset_pair
    rr, cc = np.indices((h, w))
    row_on = (rr - ro) % 2 == 0
    col_on = (cc - co) % 2 == 0
    known = row_on & col_on
    horiz = row_on & ~col_on
    vert = ~row_on & col_on
    diag = ~row_on & ~col_on
    havg = 0.5 * (np.roll(raw, 1, 1) + np.roll(raw, -1, 1))
    vavg = 0.5 * (np.roll(raw, 1, 0) + np.roll(raw, -1, 0))
    davg = 0.25 * (
        np.roll(np.roll(raw, 1, 0), 1, 1)
        + np.roll(np.roll(raw, 1, 0), -1, 1)
        + np.roll(np.roll(raw, -1, 0), 1, 1)
        + np.roll(np.roll(raw, -1, 0), -1, 1)
    )
    out = np.empty_like(raw)
    out[known] = raw[known]
    out[horiz] = havg[horiz]
    out[vert] = vavg[vert]
    out[diag] = davg[diag]
    return out[2:-2, 2:-2]


def demosaic(raw_img, green_offset, red_offset, blue_offset):
    g = interpolate_green(raw_img, green_offset)
    r = interpolate_redblue(raw_img, red_offset)
    b = interpolate_redblue(raw_img, blue_offset)
    rgb = np.stack([r, g, b], axis=-1)
    return np.clip(rgb, 0.0, 1.0)


def align_imgs(img1, img2, maxOffset=15):
    a = _to_float(img1)
    b = _to_float(img2)
    if a.ndim == 3:
        a = a.mean(axis=2)
        b = b.mean(axis=2)
    m = maxOffset
    interior_a = a[m:-m, m:-m]
    best_error = np.inf
    best_offset = (0, 0)
    for dy in range(-m, m + 1):
        for dx in range(-m, m + 1):
            shifted = np.roll(np.roll(b, dy, axis=0), dx, axis=1)
            patch = shifted[m:-m, m:-m]
            err = np.sum((interior_a - patch) ** 2)
            if err < best_error:
                best_error = err
                best_offset = (dy, dx)
    return best_offset, best_error


def combine_imgs(imgs, offset_list):
    acc = None
    n = 0
    for img, (dy, dx) in zip(imgs, offset_list):
        x = np.asarray(img).astype(np.float32)
        if x.max() > 1.5:
            x = x / 255.0
        shifted = np.roll(np.roll(x, dy, axis=0), dx, axis=1)
        acc = shifted if acc is None else acc + shifted
        n += 1
    return acc / n


def gray_world(input_img):
    img = np.asarray(input_img).astype(np.float32)
    if img.max() > 1.5:
        img = img / 255.0
    means = img.reshape(-1, 3).mean(axis=0)
    target = means[1]
    scales = target / np.maximum(means, 1e-8)
    out = img * scales
    return np.clip(out, 0.0, 1.0)


def white_patch(input_img, center=(420, 80), half=12):
    """White-patch using a window around `center`=(col, row), e.g. a cloud."""
    img = np.asarray(input_img).astype(np.float32)
    if img.max() > 1.5:
        img = img / 255.0
    x, y = center
    patch = img[y - half : y + half, x - half : x + half]
    means = patch.reshape(-1, 3).mean(axis=0)
    scales = 1.0 / np.maximum(means, 1e-8)
    out = img * scales
    return np.clip(out, 0.0, 1.0)
