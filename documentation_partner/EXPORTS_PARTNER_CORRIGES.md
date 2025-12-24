# ✅ EXPORTS PARTNER - CORRECTIONS COMPLÈTES

## 🎯 Corrections apportées

### 1. ✅ Word POS : Section DEMANDES ajoutée

**Ajout** : Nouvelle section "DEMANDES" affichant le statut POS/NEG de chaque demande

**Emplacement** : Après la section "RÉSULTATS ENQUÊTE"

**Format** :
```
═══ DEMANDES ═══
🏠 Adresse         | ✓ TROUVÉ (POS)
📞 Téléphone       | ✗ NON TROUVÉ (NEG) - Aucun téléphone trouvé
🏢 Employeur       | ✓ TROUVÉ (POS)
```

**Code ajouté** :
```python
# Section DEMANDES
requests = PartnerCaseRequest.query.filter_by(donnee_id=donnee.id).all()
if requests:
    add_row("═══ DEMANDES ═══", "", span=True)
    
    REQUEST_LABELS = {
        'ADDRESS': ('🏠', 'Adresse'),
        'PHONE': ('📞', 'Téléphone'),
        'EMPLOYER': ('🏢', 'Employeur'),
        'BANK': ('🏦', 'Banque'),
        'BIRTH': ('🎂', 'Naissance')
    }
    
    for req in requests:
        icon, label = REQUEST_LABELS.get(req.request_code, ('❓', req.request_code))
        status_text = "✓ TROUVÉ (POS)" if req.status == 'POS' else "✗ NON TROUVÉ (NEG)"
        
        demand_label = f"{icon} {label}"
        if req.status == 'NEG' and req.memo:
            demand_value = f"{status_text} - {req.memo[:80]}"
        else:
            demand_value = status_text
        
        add_row(demand_label, demand_value, bold_label=False)
```

**Avantages** :
- ✅ Affiche clairement chaque demande et son statut
- ✅ Inclut le mémo pour les demandes NEG
- ✅ Icônes visuels (🏠📞🏢🏦🎂)
- ✅ Format compact (1 page par enquête maintenu)

---

### 2. ✅ Excel POS : Tarif combiné

**Problème** : Utilisait uniquement le tarif de la lettre (ex: A = 15€)

**Solution** : Utilise maintenant `PartnerTarifResolver` pour calculer le tarif selon la lettre + les demandes

**Exemple** :
- Lettre A + ADDRESS = 15€
- Lettre A + ADDRESS + EMPLOYER = 25€
- Lettre W + ADDRESS + EMPLOYER + BANK = 50€

**Code modifié** :
```python
# AVANT
montant = self._get_montant_from_tarif(donnee.tarif_lettre)

# APRÈS
try:
    resolver = PartnerTarifResolver()
    montant = resolver.resolve_tarif(donnee, self.client_id)
    if montant is None:
        # Fallback : utiliser le tarif simple si pas de règle combinée
        montant = self._get_montant_from_tarif(donnee.tarif_lettre)
        logger.warning(f"Pas de tarif combiné, utilisation tarif simple")
except Exception as e:
    logger.error(f"Erreur calcul tarif combiné: {e}")
    montant = self._get_montant_from_tarif(donnee.tarif_lettre)
```

**Sécurités** :
- ✅ Fallback sur tarif simple si pas de règle combinée trouvée
- ✅ Gestion des erreurs avec logs
- ✅ Ne jamais retourner 0 silencieusement

**Colonnes Excel POS** :
- ✅ "Date naissance (MAJ)" : depuis `donnee.dateNaissance_maj`
- ✅ "Lieu naissance (MAJ)" : depuis `donnee.lieuNaissance_maj`
- ✅ "Montant facture" : tarif combiné résolu

---

### 3. ✅ Excel NEG : Erreur corrigée

**Problème** : `JOIN` échouait si certains dossiers n'avaient pas de `DonneeEnqueteur`

**Solution** : Utilise `OUTER JOIN` pour gérer tous les cas

**Code modifié** :
```python
# AVANT (provoquait une erreur)
query = query.join(Donnee.donnee_enqueteur).filter(
    db.or_(
        db.text("donnees_enqueteur.code_resultat IN ('N', 'I')")
    )
)

# APRÈS (robuste)
query = query.outerjoin(DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id).filter(
    db.or_(
        DonneeEnqueteur.code_resultat.in_(['N', 'I']),
        DonneeEnqueteur.id == None  # Dossiers sans enquêteur = NEG
    )
)
```

**Avantages** :
- ✅ Gère les dossiers sans `DonneeEnqueteur`
- ✅ Ne provoque plus d'erreur
- ✅ Génère toujours un fichier (même vide avec headers)

---

## 📊 Tests à effectuer

### Test 1 : Word POS avec demandes
1. Valider une enquête PARTNER avec RECHERCHE = "ADRESSE EMPLOYEUR"
2. Ajouter une adresse trouvée (→ ADDRESS POS)
3. Ne PAS ajouter d'employeur (→ EMPLOYER NEG)
4. Exporter Word POS
5. ✅ Vérifier que la section "DEMANDES" affiche :
   - 🏠 Adresse : ✓ TROUVÉ (POS)
   - 🏢 Employeur : ✗ NON TROUVÉ (NEG) - Aucune information employeur trouvée

### Test 2 : Excel POS avec tarif combiné
1. Créer une règle de tarif :
   - Lettre W + ADDRESS = 15€
   - Lettre W + ADDRESS + EMPLOYER = 30€
2. Importer un dossier avec TARIF = W, RECHERCHE = "ADRESSE EMPLOYEUR"
3. Ajouter adresse + employeur
4. Valider
5. Exporter Excel POS
6. ✅ Vérifier que "Montant facture" = 30€ (et non 15€)

### Test 3 : Excel NEG sans erreur
1. Valider une enquête PARTNER comme NEG (résultat N)
2. Exporter Excel NEG
3. ✅ Pas d'erreur
4. ✅ Fichier généré avec headers même si 0 ligne

---

## 📁 Fichiers modifiés

✅ `backend/services/partner_export_service.py`
- Ajout imports : `PartnerCaseRequest`, `PartnerTarifResolver`
- Méthode `generate_enquetes_positives_word()` : Section DEMANDES
- Méthode `generate_enquetes_positives_excel()` : Tarif combiné

✅ `backend/routes/partner_export.py`
- Méthode `export_enquetes_negatives()` : OUTER JOIN robuste

---

## 🚀 Prochaines étapes

### Pour tester maintenant
1. **Redémarrer le backend** (si pas déjà fait)
2. **Valider une enquête PARTNER**
3. **Exporter** : Word POS + Excel POS
4. **Vérifier** :
   - Section DEMANDES dans Word
   - Tarif correct dans Excel
   - Pas d'erreur sur export NEG

### Si tout fonctionne
- ✅ Phase 7 complétée !
- ⏭️ Phase 8 : Tests finaux (import, exports, non-régression EOS)

---

**Date :** 23/12/2025  
**Statut :** ✅ Corrections complètes  
**Temps estimé pour tests :** 10-15 minutes

