<?php

namespace App\Utils;

class FakeImageUtil
{
    public static function imagePath($height = 400, $width = 400): string
    {
        $imagePath = "https://picsum.photos/$height/$width";

        return $imagePath;
    }
}
