<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;

require '../phpmailer/src/PHPMailer.php';
require '../phpmailer/src/SMTP.php';
require '../phpmailer/src/Exception.php';

class EmailManager {
    private $to;
    private $subject;
    private $message;

    public function __construct($to, $subject, $message) {
        $this->to = $to;
        $this->subject = $subject;
        $this->message = $message;
    }

    public function sendEmail() {
        $mail = new PHPMailer(true);

        try {
            // Server settings
            $mail->SMTPDebug = SMTP::DEBUG_OFF;
            $mail->isSMTP();
            $mail->Host = 'smtp.gmail.com';
            $mail->SMTPAuth = true;
            $mail->Username = 'diptimeghare123@gmail.com';
            $mail->Password = 'pzay fflu ikyt yjcs'; // Use app-specific password for Gmail
            $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
            $mail->Port = 587;

            // Recipients
            $mail->setFrom('diptimeghare123@gmail.com', 'Takeit Ideas');
            $mail->addAddress($this->to);

            // Content
            $mail->isHTML(true);
            $mail->Subject = $this->subject;
            $mail->Body = $this->message;
            $mail->AltBody = strip_tags($this->message);

            $mail->send();
            return true;
        } catch (Exception $e) {
            return false;
        }
    }
}
?>
