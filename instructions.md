# Instructions pour créer un dépôt GitHub manuellement

1. Connectez-vous à GitHub : Rendez-vous sur https://github.com et connectez-vous à votre compte.

2. Créez un nouveau dépôt :
   - Cliquez sur le bouton "New repository" en haut à droite.
   - Entrez un nom pour votre dépôt (ex: taxi_be_ako).
   - Choisissez la visibilité (public ou privé).
   - Ajoutez une description (ex: "Projet de gestion de taxis").

3. Initialisez le dépôt localement :
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. Liez le dépôt local à GitHub :
   ```bash
   git remote add origin https://github.com/votre-username/taxi_be_ako.git
   ```
   Remplacez votre-username par votre nom d'utilisateur GitHub.

5. Poussez les fichiers vers GitHub :
   ```bash
   git push -u origin main
   ```

6. Vérifiez le dépôt : Votre dépôt devrait maintenant être visible sur GitHub avec tous les fichiers du projet.
