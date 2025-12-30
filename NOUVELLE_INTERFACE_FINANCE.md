# 📊 Nouvelle Interface Finance - Guide Utilisateur

## 🎯 Ce qui a changé

### Avant (❌ Confus)
Il y avait **3 onglets séparés** dans le menu principal :
- "Tarification" - pour gérer les tarifs
- "Paiements Enquêteurs" - pour payer les enquêteurs  
- "Rapports Financiers" - pour voir les gains

**Problème** : Trop de choses éparpillées, difficile de comprendre où aller.

### Maintenant (✅ Simple et Clair)
Un seul onglet **"Finance & Paiements"** avec **3 grandes cartes** :

```
┌──────────────────────────────────────────────────────────────┐
│              Finance & Paiements                              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   💰 Gains   │  │  👥 Paiements │  │  ⚙️ Tarifs   │      │
│  │Administrateur│  │  Enquêteurs  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## 📋 Les 3 Sections Expliquées

### 1️⃣ **Gains Administrateur** 💰

**À quoi ça sert ?**  
Voir combien **l'entreprise (EOS)** a gagné en facturant les clients, et combien elle a dépensé en payant les enquêteurs.

**Ce qu'on voit :**
- 💵 **Total Facturé** : Tout l'argent qu'EOS a facturé aux clients (EOS et PARTNER)
- 💸 **Total Enquêteurs** : Tout l'argent versé aux enquêteurs
- 📈 **Marge** : La différence = le profit d'EOS

**Filtre important :**  
Vous pouvez choisir :
- **Tous les clients** : Vue globale
- **EOS** : Seulement les enquêtes clients EOS
- **PARTNER** : Seulement les enquêtes clients PARTNER

**Exemple concret :**
```
Si vous sélectionnez "EOS" :
- Total Facturé : 50 000 € (ce qu'EOS a facturé à ses clients)
- Total Enquêteurs : 35 000 € (ce qu'EOS a payé aux enquêteurs)
- Marge : 15 000 € (le profit d'EOS)
```

---

### 2️⃣ **Paiements Enquêteurs** 👥

**À quoi ça sert ?**  
Voir combien **chaque enquêteur** a gagné et lui faire ses paiements.

**Ce qu'on voit :**
- Liste de tous les enquêteurs
- Pour chaque enquêteur :
  - ✅ **Total Gagné** : Montant total de toutes ses enquêtes confirmées
  - 💳 **Déjà Payé** : Ce qu'on lui a déjà versé
  - ⏳ **Reste à Payer** : Ce qu'il faut encore lui verser

**Actions possibles :**
- Cliquer sur un enquêteur → Voir le détail de ses gains
- Cocher des lignes → "Marquer comme payé"

**Filtre important :**  
Vous pouvez choisir de voir les gains EOS ou PARTNER séparément.

**Exemple concret :**
```
Jean Dupont :
- Total Gagné : 5 000 € (de 50 enquêtes)
- Déjà Payé : 3 000 € (paiement du 15/12)
- Reste à Payer : 2 000 € (à verser)
```

---

### 3️⃣ **Gérer les Tarifs** ⚙️

**À quoi ça sert ?**  
Configurer **les prix** pour chaque type d'enquête.

**Les 3 types de tarifs :**

#### 📋 Tarifs EOS
Prix qu'**EOS facture à ses clients** :
- `A` = Adresse seule → 8 €
- `AT` = Adresse + Téléphone → 22 €
- `ATB` = Adresse + Téléphone + Banque → 24 €
- etc.

#### 👤 Tarifs Enquêteur
Montant qu'**on verse à l'enquêteur** :
- `A` = Adresse seule → 5,60 €
- `AT` = Adresse + Téléphone → 15,40 €
- `ATB` = Adresse + Téléphone + Banque → 16,80 €
- etc.

#### 🤝 Tarifs PARTNER
Pour les clients PARTNER, c'est différent : on utilise des **lettres** (W, X, Y, Z...).  
Vous définissez le prix pour chaque lettre.

**Exemple :**
- Lettre `W` → 50 €
- Lettre `X` → 75 €
- etc.

---

## 🚀 Comment Utiliser la Nouvelle Interface

### Scénario 1 : "Je veux voir combien EOS a gagné ce mois-ci"

1. Cliquez sur l'onglet **"Finance & Paiements"**
2. Cliquez sur la carte **"Gains Administrateur"** (💰)
3. En haut à droite, sélectionnez :
   - **"Tous les clients"** pour le total
   - **"EOS"** pour voir seulement EOS
   - **"PARTNER"** pour voir seulement PARTNER
4. Regardez les graphiques et les chiffres

---

### Scénario 2 : "Je veux payer Jean Dupont"

1. Cliquez sur l'onglet **"Finance & Paiements"**
2. Cliquez sur la carte **"Paiements Enquêteurs"** (👥)
3. Trouvez Jean Dupont dans la liste
4. Cochez les lignes à payer
5. Cliquez sur **"Marquer comme payé"**
6. Entrez la référence de paiement (ex: virement du 24/12)

---

### Scénario 3 : "Je veux modifier le tarif AT"

1. Cliquez sur l'onglet **"Finance & Paiements"**
2. Cliquez sur la carte **"Gérer les Tarifs"** (⚙️)
3. Cliquez sur l'onglet **"📋 Tarifs EOS"** ou **"👤 Tarifs Enquêteur"**
4. Trouvez la ligne `AT`
5. Cliquez sur le bouton ✏️ (éditer)
6. Modifiez le montant
7. Cliquez sur ✅ (valider)

---

## 💡 Conseils d'Utilisation

### Pour la comptabilité mensuelle :
1. Allez dans **"Gains Administrateur"**
2. Regardez le mois actuel
3. Exportez le rapport (bouton en haut à droite)

### Pour les paiements mensuels :
1. Allez dans **"Paiements Enquêteurs"**
2. Regardez la colonne **"Reste à Payer"**
3. Cochez tous les enquêteurs à payer
4. Faites le virement bancaire
5. Marquez comme payé avec la référence du virement

### Pour vérifier un tarif :
1. Allez dans **"Gérer les Tarifs"**
2. Choisissez l'onglet approprié (EOS, Enquêteur ou PARTNER)
3. Consultez ou modifiez les tarifs

---

## ❓ Questions Fréquentes

### Q : Où sont passés les anciens onglets ?
**R :** Ils sont tous regroupés dans **"Finance & Paiements"** avec 3 cartes claires.

### Q : Comment voir combien EOS a gagné vs PARTNER ?
**R :** Allez dans **"Gains Administrateur"** et utilisez le filtre en haut à droite pour sélectionner "EOS" ou "PARTNER".

### Q : Est-ce que les montants changent après confirmation ?
**R :** **Non** ! Une fois une enquête confirmée, les montants sont **figés**. Même si vous modifiez les tarifs plus tard, les enquêtes déjà confirmées gardent leurs montants.

### Q : Puis-je modifier un montant après avoir payé ?
**R :** **Non** ! Une fois marqué comme "payé", le montant est **verrouillé** pour éviter les erreurs.

### Q : Comment savoir si un enquêteur a été payé ?
**R :** Dans **"Paiements Enquêteurs"**, regardez la colonne **"Déjà Payé"**. Vous pouvez aussi cliquer sur l'enquêteur pour voir l'historique détaillé.

---

## 📊 Résumé Visuel

```
┌─────────────────────────────────────────────────────────┐
│  Finance & Paiements                                    │
└─────────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌───────┐   ┌───────┐   ┌───────┐
    │ Gains │   │Paiemen│   │Tarifs │
    │ Admin │   │  ts   │   │       │
    └───────┘   └───────┘   └───────┘
        │           │           │
        │           │           │
        ▼           ▼           ▼
   Combien     Combien      Configurer
   EOS a      enquêteurs     les prix
   gagné?     à payer?
```

---

## ✅ Avantages de la Nouvelle Interface

| Avant | Maintenant |
|-------|------------|
| ❌ 3 onglets séparés | ✅ 1 seul onglet clair |
| ❌ Difficile de trouver où aller | ✅ 3 cartes explicites |
| ❌ Mélange EOS et PARTNER | ✅ Filtre pour séparer |
| ❌ Confusion sur qui a gagné quoi | ✅ Sections claires : Admin vs Enquêteurs |

---

## 🎉 Conclusion

La nouvelle interface **"Finance & Paiements"** simplifie tout :
- ✅ **Plus simple** : Tout au même endroit
- ✅ **Plus clair** : 3 cartes avec des rôles précis
- ✅ **Plus rapide** : Moins de clics pour trouver l'info
- ✅ **Plus sûr** : Montants figés après confirmation et paiement

**Profitez de la nouvelle interface ! 🚀**



