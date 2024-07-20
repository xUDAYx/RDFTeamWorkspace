<?php

class User {
    private $file;

    public function __construct() {
        $this->file = '../RDF_DATA/signUpDetailsData.json';
    }

    public function fetchUserByEmail($email) {
        if (!file_exists($this->file)) {
            return null;
        }

        $fileContents = file_get_contents($this->file);
        $current_data = json_decode($fileContents, true);

        foreach ($current_data as $user) {
            if ($user['email'] === $email) {
                return $user;
            }
        }

        return null;
    }
}
?>
