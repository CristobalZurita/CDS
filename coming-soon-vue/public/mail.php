<?php
/**
 * CDS Coming Soon — Mailer
 * Recibe POST desde Vue y envía a cirujanodesintetizadores@gmail.com
 */

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');

// Solo POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Método no permitido']);
    exit;
}

// Datos del formulario (sanitizados)
$name       = trim(strip_tags($_POST['name']       ?? ''));
$email      = trim(strip_tags($_POST['email']      ?? ''));
$instrument = trim(strip_tags($_POST['instrument'] ?? ''));
$message    = trim(strip_tags($_POST['message']    ?? ''));

// Validación básica
if (!$name || !$message || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Datos inválidos']);
    exit;
}

$to      = 'cirujanodesintetizadores@gmail.com';
$subject = "=?UTF-8?B?" . base64_encode("Contacto web: $name") . "?=";
$replyTo = str_replace(["\r", "\n"], '', $email);

// Cuerpo del correo
$body  = "Nombre:      $name\n";
$body .= "Email:       $email\n";
if ($instrument) {
    $body .= "Instrumento: $instrument\n";
}
$body .= "\nMensaje:\n$message\n";
$body .= "\n---\nEnviado desde cirujanodesintetizadores.cl";

// Cabeceras
$headers  = "From: noreply@cirujanodesintetizadores.cl\r\n";
$headers .= "Reply-To: $replyTo\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "X-Mailer: PHP/" . phpversion() . "\r\n";

if (mail($to, $subject, $body, $headers)) {
    echo json_encode(['ok' => true]);
} else {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Error al enviar el correo']);
}
