export const resolveImagePath = (src, prefix = '/storage/') => {
    if (typeof (src) === 'string') {
        if (src.startsWith('http')) return src;
        return prefix + src;
    }
}

export const resolveImagePathRaw = (src) => {
    if (typeof (src) == 'string') {
        if (src.startsWith('http')) return src;
        return src;
    }
}

export const fakeImagePath = function(height = 400, width = 400) {
    return `https://picsum.photos/${height}/${width}`
}
