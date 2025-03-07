# Guide de connexion pour les enquêteurs

## Prérequis
1. Installer OpenVPN sur votre ordinateur
   - Windows : Téléchargez depuis https://openvpn.net/community-downloads/
   - Mac : Téléchargez depuis https://openvpn.net/client-connect-vpn-for-mac-os/
   - Linux : `sudo apt-get install openvpn` ou équivalent

## Étapes de connexion

1. Installation du certificat VPN
   - Ouvrez le fichier .ovpn qui vous a été fourni avec OpenVPN
   - Acceptez la connexion quand elle vous est proposée

2. Connexion à l'application
   - Une fois connecté au VPN, ouvrez votre navigateur
   - Accédez à l'adresse : http://192.168.150.107:5173
   - Vous devriez voir l'interface de l'application EOS

## En cas de problème

1. Vérifiez votre connexion VPN :
   - Ouvrez une invite de commande
   - Tapez : `ping 192.168.150.107`
   - Si vous recevez une réponse, la connexion VPN est active

2. Si vous ne pouvez pas vous connecter :
   - Vérifiez que OpenVPN est bien lancé
   - Essayez de reconnecter le VPN
   - Contactez le support technique

## Support

En cas de problème, contactez le support technique :
- Email : [adresse email du support]
- Téléphone : [numéro du support]
