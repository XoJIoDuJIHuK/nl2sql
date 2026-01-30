# System Prompts

This directory contains modular system prompts for the NL2SQL system.

## Structure

```
system_prompts/
├── CommonPrompt.md          # Shared mathematical model and definitions
├── SQLSpecificPrompt.md     # SQL-specific rules, schemas, and API specs
├── GraphQLSpecificPrompt.md # GraphQL-specific rules and mappings
├── SystemPrompt.md          # Composed full prompt for SQL (generated)
└── GraphQLSystemPrompt.md   # Composed full prompt for GraphQL (generated)
```

## Components

### CommonPrompt.md
Contains the mathematical model of the industrial cluster:
- Formal definitions of sets (R, R̄, etc.)
- Axioms for the system
- Abbreviations and terminology
- Formal product definitions (final, intermediate, internal consumption only)

### SQLSpecificPrompt.md
Contains SQL-specific instructions:
- SQL Server compatibility rules
- Database schema definitions
- AP (Application Server) API specifications
- SQL query formatting rules
- Translation rules for NL→SQL

### GraphQLSpecificPrompt.md
Contains GraphQL-specific instructions:
- GraphQL introspection guidelines
- Mapping of mathematical model to GraphQL schema
- GraphQL query examples
- How to identify products for internal vs external consumption

## Composed Prompts

### SystemPrompt.md (for SQL)
= CommonPrompt.md + SQLSpecificPrompt.md

### GraphQLSystemPrompt.md (for GraphQL)
= CommonPrompt.md + GraphQLSpecificPrompt.md

## Usage

Run the composition script from the project root:

```bash
# Compose all prompts
python3 compose_prompts.py

# Compose only SQL prompt
python3 compose_prompts.py --sql

# Compose only GraphQL prompt
python3 compose_prompts.py --graphql
```

## Why Modular?

The modular structure ensures:
1. **Consistency**: Both SQL and GraphQL prompts share the same mathematical model definitions
2. **Maintainability**: Changes to the mathematical model only need to be made in CommonPrompt.md
3. **Clarity**: Each specific prompt focuses only on its relevant technology
4. **Flexibility**: Easy to add new prompt types (e.g., REST API prompts)

## Key Definitions

### Set R
All products in the cluster. In GraphQL: `products` query.

### Set R̄ (R-bar)
Products for external consumers (exported outside the cluster). 
- In SQL: Products with entries in `plan_values` table
- In GraphQL: Products with entries in `planValues` query

### Set R \ R̄
Products only for internal consumption.
- Definition: Products in R but NOT in R̄
- In GraphQL: Products that have no entries in `planValues`

### Technological Chains (overline{overline{R}})
Production relationships between products.
- In SQL: `production_chains` table
- In GraphQL: `productionChains` query
