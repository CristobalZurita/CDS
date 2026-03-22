<?php

namespace App\Traits;

trait HasCustomLogger
{
    public function logThisMethod(): void
    {
        $backtrace = debug_backtrace();
        $trait = __TRAIT__;
        $class = $backtrace[1]['class'];
        $method = $backtrace[1]['function'];
        $message = "{$trait} method called from {$class}::{$method}";
        logger()->info($message);
    }
}
