//! Parses SQL text into a syntax tree.

/// A parsed statement.
pub struct Query { pub tokens: Vec<String> }

/// Split SQL into whitespace tokens (placeholder for a real lexer).
pub fn parse(sql: &str) -> Query {
    Query { tokens: sql.split_whitespace().map(str::to_owned).collect() }
}
