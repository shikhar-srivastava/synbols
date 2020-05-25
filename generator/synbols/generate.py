import time as t
import logging
import numpy as np

from .drawing import Camouflage, Gradient, Image, NoPattern, SolidColor, Symbol, MultiGradient
from .fonts import ALPHABET_MAP


def _select(default, value, rng):
    if value is None:
        return default
    elif callable(value):
        return value(rng)
    else:
        return value


# ya basic!
def basic_image_sampler(alphabet=None, char=None, font=None, background=None, foreground=None, is_slant=None,
                        is_bold=None, rotation=None, scale=None, translation=None, inverse_color=None,
                        pixel_noise_scale=0.01, resolution=(32, 32), is_gray=False, n_symbols=1, rng=np.random):
    def sampler():
        symbols = []
        _n_symbols = _select(1, n_symbols, rng)
        for i in range(_n_symbols):
            _alphabet = _select(rng.choice(list(ALPHABET_MAP.values())), alphabet, rng)
            _char = _select(rng.choice(_alphabet.symbols), char, rng)
            _font = _select(rng.choice(_alphabet.fonts), font, rng)
            _is_bold = _select(rng.choice([True, False]), is_bold, rng)
            _is_slant = _select(rng.choice([True, False]), is_slant, rng)
            _rotation = _select(rng.randn() * 0.3, rotation, rng)
            _scale = _select(0.6 * np.exp(rng.randn() * 0.2), scale, rng)
            _translation = _select(tuple(rng.rand(2) * 1.8 - 0.9), translation, rng)
            _foreground = _select(Gradient(rng=rng), foreground, rng)

            symbols.append(Symbol(alphabet=_alphabet, char=_char, font=_font, foreground=_foreground,
                                  is_slant=_is_slant, is_bold=_is_bold, rotation=_rotation, scale=_scale,
                                  translation=_translation, rng=rng))

        _background = _select(Gradient(rng=rng), background, rng)
        _inverse_color = _select(rng.choice([True, False]), inverse_color, rng)

        return Image(symbols, background=_background, inverse_color=_inverse_color, resolution=resolution,
                     pixel_noise_scale=pixel_noise_scale, is_gray=is_gray, rng=rng)

    return sampler


def flatten_mask(masks):
    overlap = np.mean(masks.sum(axis=-1) >= 256)

    flat_mask = np.zeros(masks.shape[:-1])

    for i in range(masks.shape[-1]):
        flat_mask[(masks[:, :, i] > 2)] = i + 1
    return flat_mask, {'overlap_score': overlap}


def flatten_mask_except_first(masks):
    return np.stack((masks[:, :, 0], flatten_mask(masks[:, :, 1:])), axis=2)


def add_occlusion(attr_sampler, n_occlusion=None, occlusion_char=None, rotation=None, scale=None, translation=None,
                  foreground=None, rng=np.random):
    occlusion_chars = ['■', '▲', '●']

    def sampler():
        image = attr_sampler()
        _n_occlusion = _select(rng.randint(1, 5), n_occlusion, rng)

        for i in range(_n_occlusion):
            _scale = _select(0.3 * np.exp(rng.randn() * 0.1), scale, rng)
            _translation = _select(tuple(rng.rand(2) * 3 - 1.5), translation, rng)

            _occlusion_char = _select(rng.choice(occlusion_chars), occlusion_char, rng)
            _rotation = _select(rng.rand() * np.pi * 2, rotation, rng)
            _foreground = _select(Gradient(rng=rng), foreground, rng)

            occlusion = Symbol(ALPHABET_MAP['latin'], _occlusion_char, font='Arial', foreground=_foreground,
                               rotation=_rotation, scale=_scale, translation=_translation, is_slant=False,
                               is_bold=False)
            image.add_symbol(occlusion)

        return image

    return sampler


def dataset_generator(attr_sampler, n_samples, mask_aggregator=None):
    """High level function generating the dataset from an attribute generator."""
    t0 = t.time()
    for i in range(n_samples):
        attributes = attr_sampler()
        mask = attributes.make_mask()
        x = attributes.make_image()
        y = attributes.attribute_dict()

        if mask_aggregator is not None:
            mask = mask_aggregator(mask)
            if isinstance(mask, tuple):
                mask, mask_attributes = mask
                y.update(mask_attributes)

        if i % 100 == 0 and i != 0:
            dt = (t.time() - t0) / 100.
            eta = (n_samples - i) * dt
            eta_str = t.strftime("%Hh%Mm%Ss", t.gmtime(eta))

            logging.info("generating sample %4d / %d (%.3g s/image) ETA: %s", i, n_samples, dt, eta_str)
            # print("generating sample %4d / %d (%.3g s/image) ETA: %s"%(i, n_samples, dt, eta_str))
            t0 = t.time()
        yield x, mask, y


def generate_char_grid(alphabet_name, n_char, n_font, rng=np.random, **kwargs):
    def _attr_generator():
        alphabet = ALPHABET_MAP[alphabet_name]

        chars = rng.choice(alphabet.symbols, n_char, replace=False)
        fonts = rng.choice(alphabet.fonts, n_font, replace=False)
        for char in chars:
            for font in fonts:
                yield basic_image_sampler(alphabet, char=char, font=font, rng=rng, **kwargs)()

    return dataset_generator(_attr_generator().__next__, n_char * n_font, flatten_mask)


def generate_plain_dataset(n_samples, alphabet='latin', **kwargs):
    alphabet = ALPHABET_MAP[alphabet]
    attr_sampler = basic_image_sampler(
        alphabet=alphabet, background=NoPattern(), foreground=SolidColor((1, 1, 1,)), is_slant=False,
        is_bold=False, rotation=0, scale=1., translation=(0., 0.), inverse_color=False, pixel_noise_scale=0.)
    return dataset_generator(attr_sampler, n_samples)


def generate_tiny_dataset(n_samples, alphabet='latin', **kwarg):
    fg = SolidColor((1, 1, 1))
    bg = SolidColor((0, 0, 0))
    attr_sampler = basic_image_sampler(alphabet=ALPHABET_MAP[alphabet], background=bg, foreground=fg, is_bold=False,
                                       is_slant=False, scale=1, resolution=(8, 8), is_gray=True)
    return dataset_generator(attr_sampler, n_samples)


def generate_default_dataset(n_samples, alphabet='latin', **kwarg):
    attr_sampler = basic_image_sampler(alphabet=ALPHABET_MAP[alphabet])
    return dataset_generator(attr_sampler, n_samples)


def make_preview(generator, file_name, n_row=20, n_col=40):
    x_list = []
    y_list = []
    for x, mask, y in generator:

        if x_list is not None:

            x_list.append(x)
            y_list.append(y)

            if len(x_list) == n_row * n_col:
                logging.info("Generating Preview")
                from view_dataset import plot_dataset
                from matplotlib import pyplot as plt
                plot_dataset(np.stack(x_list), y_list, h_axis=None, v_axis=None, n_row=n_row, n_col=n_col)
                x_list = None
                # TODO make te dpi dependent on the total number of pixels
                plt.savefig(file_name, dpi=1000, bbox_inches='tight', pad_inches=0)

        yield x, mask, y


def generate_camouflage_dataset(n_samples, alphabet='latin', **kwarg):
    def attr_sampler():
        angle = np.random.rand() * np.pi * 2
        angle = 0
        fg = Camouflage(stroke_angle=angle, stroke_width=0.1, stroke_length=0.6, stroke_noise=0)
        bg = Camouflage(stroke_angle=angle + np.pi / 2, stroke_width=0.1, stroke_length=0.6, stroke_noise=0)
        # scale = 0.7 * np.exp(np.random.randn() * 0.1)
        scale = 0.8
        return basic_image_sampler(
            alphabet=ALPHABET_MAP[alphabet], background=bg, foreground=fg, is_bold=True, is_slant=False,
            scale=scale)()

    return dataset_generator(attr_sampler, n_samples)


# for segmentation, detection, counting
# -------------------------------------

def generate_segmentation_dataset(n_samples, alphabet='latin', resolution=(128, 128), **kwarg):
    def scale(rng):
        return 0.1 * np.exp(rng.randn() * 0.4)

    def n_symbols(rng):
        return rng.choice(list(range(3, 10)))

    attr_generator = basic_image_sampler(alphabet=ALPHABET_MAP[alphabet], resolution=resolution, scale=scale,
                                         is_bold=False, n_symbols=n_symbols)
    return dataset_generator(attr_generator, n_samples, flatten_mask)




def generate_counting_dataset(n_samples, alphabet='latin', resolution=(128, 128), scale_variation=0.5, **kwarg):
    def scale(rng):
        return 0.1 * np.exp(rng.randn() * scale_variation)

    def n_symbols(rng):
        return rng.choice(list(range(3, 10)))

    def char_sampler(rng):
        if rng.rand() < 0.3:
            return rng.choice(ALPHABET_MAP[alphabet].symbols)
        else:
            return 'a'

    attr_generator = basic_image_sampler(alphabet=ALPHABET_MAP[alphabet], char=char_sampler, resolution=resolution,
                                         scale=scale, is_bold=False, n_symbols=n_symbols)
    return dataset_generator(attr_generator, n_samples, flatten_mask)


def generate_counting_dataset_scale_fix(n_samples, **kwargs):
    return generate_counting_dataset(n_samples, scale_variation=0, **kwargs)


def generate_counting_dataset_crowded(n_samples, alphabet='latin', resolution=(128, 128), scale_variation=0.1, **kwarg):
    def scale(rng):
        return 0.1 * np.exp(rng.randn() * scale_variation)

    def n_symbols(rng):
        return rng.choice(list(range(30, 50)))

    def char_sampler(rng):
        if rng.rand() < 0.3:
            return rng.choice(ALPHABET_MAP[alphabet].symbols)
        else:
            return 'a'

    attr_generator = basic_image_sampler(alphabet=ALPHABET_MAP[alphabet], char=char_sampler, resolution=resolution,
                                         scale=scale, is_bold=False, n_symbols=n_symbols)
    return dataset_generator(attr_generator, n_samples, flatten_mask)

# for few-shot learning
# ---------------------

def all_chars(n_samples, **kwarg):
    symbols_list = []
    for alphabet in ALPHABET_MAP.values():
        symbols = alphabet.symbols[:200]
        logging.info("Using %d/%d symbols from alphabet %s", len(symbols), len(alphabet.symbols), alphabet.name)
        symbols_list.extend(zip(symbols, [alphabet] * len(symbols)))

    def attr_sampler():
        char, alphabet = symbols_list[np.random.choice(len(symbols_list))]
        return basic_image_sampler(alphabet=alphabet, char=char)()

    return dataset_generator(attr_sampler, n_samples)


def all_fonts(n_samples, **kwarg):
    font_list = []
    for alphabet in ALPHABET_MAP.values():
        fonts = alphabet.fonts[:500]
        logging.info("Using %d/%d fonts from alphabet %s", len(fonts), len(alphabet.fonts), alphabet.name)

        font_list.extend(zip(fonts, [alphabet] * len(fonts)))

    def attr_sampler():
        font, alphabet = font_list[np.random.choice(len(font_list))]
        return basic_image_sampler(alphabet=alphabet, font=font, is_bold=False, is_slant=False)()

    return dataset_generator(attr_sampler, n_samples)


# for active learning
# -------------------

def generate_large_translation(n_samples, alphabet='latin', **kwarg):
    attr_sampler = basic_image_sampler(alphabet=ALPHABET_MAP[alphabet], scale=0.5,
                                       translation=lambda rng: tuple(rng.rand(2) * 4 - 2))
    return dataset_generator(attr_sampler, n_samples)


def missing_symbol_dataset(n_samples, alphabet='latin', **kwarg):
    bg = MultiGradient(alpha=0.5, n_gradients=2, types=('linear', 'radial'))

    def tr(rng):
        if rng.rand() > 0.1:
            return tuple(rng.rand(2) * 2 - 1)
        else:
            return 10

    attr_generator = basic_image_sampler(alphabet=ALPHABET_MAP[alphabet], translation=tr, background=bg)
    return dataset_generator(attr_generator, n_samples)


def generate_some_large_occlusions(n_samples, alphabet='latin', **kwarg):
    def n_occlusion(rng):
        if rng.rand() < 0.2:
            return 1
        else:
            return 0

    attr_sampler = add_occlusion(basic_image_sampler(alphabet=ALPHABET_MAP[alphabet]),
                                 n_occlusion=n_occlusion,
                                 scale=lambda rng: 0.6 * np.exp(rng.randn() * 0.1),
                                 translation=lambda rng: tuple(rng.rand(2) * 6 - 3))
    return dataset_generator(attr_sampler, n_samples, flatten_mask_except_first)


def generate_many_small_occlusions(n_samples, alphabet='latin', **kwarg):
    attr_sampler = add_occlusion(basic_image_sampler(alphabet=ALPHABET_MAP[alphabet]),
                                 n_occlusion=lambda rng: rng.randint(0, 5))
    return dataset_generator(attr_sampler, n_samples, flatten_mask_except_first)


# for font classification
# -----------------------

def less_variations(n_samples, alphabet='latin', **kwarg):
    attr_generator = basic_image_sampler(
        alphabet=ALPHABET_MAP[alphabet], is_bold=False, is_slant=False,
        scale=lambda rng: 0.5 * np.exp(rng.randn() * 0.1),
        rotation=lambda rng: rng.randn() * 0.1)
    return dataset_generator(attr_generator, n_samples)


DATASET_GENERATOR_MAP = {
    'plain': generate_plain_dataset,
    'default': generate_default_dataset,
    'camouflage': generate_camouflage_dataset,
    'segmentation': generate_segmentation_dataset,
    'counting': generate_counting_dataset,
    'counting-fix-scale': generate_counting_dataset_scale_fix,
    'counting-crowded': generate_counting_dataset_crowded,
    'missing-symbol': missing_symbol_dataset,
    'some-large-occlusion': generate_some_large_occlusions,
    'many-small-occlusion': generate_many_small_occlusions,
    'large-translation': generate_large_translation,
    'tiny': generate_tiny_dataset,
    'all-fonts': all_fonts,
    'all-chars': all_chars,
    'less-variations': less_variations,
}
