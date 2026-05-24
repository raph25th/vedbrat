def resolve_document_flow_type(client_type: str, deal_direction: str) -> str:
    mapping = {
        ("physical_person", "crypto"): "agency_contract_crypto_physical",
        ("individual_entrepreneur", "crypto"): "agency_contract_crypto_ie",
        ("legal_entity", "crypto"): "agency_contract_crypto_legal",
        ("physical_person", "cars"): "agency_contract_cars_physical",
        ("legal_entity", "cars"): "agency_contract_cars_legal",
        ("physical_person", "cfa"): "offer_join_statement",
        ("individual_entrepreneur", "cfa"): "agency_contract_cfa_ie",
        ("legal_entity", "cfa"): "agency_contract_cfa_legal",
        ("physical_person", "ved"): "ved_contract_physical",
        ("individual_entrepreneur", "ved"): "ved_contract_ie",
        ("legal_entity", "ved"): "ved_contract_legal",
    }
    return mapping.get((client_type, deal_direction), "custom_manual")


def find_matching_document_templates(db, deal, requested_document_type, template_model):
    exact = (
        db.query(template_model)
        .filter(
            template_model.is_active.is_(True),
            template_model.document_flow_type == deal.document_flow_type,
            template_model.document_type == requested_document_type,
        )
        .all()
    )
    if exact:
        return exact

    return (
        db.query(template_model)
        .filter(
            template_model.is_active.is_(True),
            template_model.direction == deal.deal_direction,
            template_model.document_type == requested_document_type,
            template_model.client_type.in_([deal.client_type, "any"]),
        )
        .all()
    )
