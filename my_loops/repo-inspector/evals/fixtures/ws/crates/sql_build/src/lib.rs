//! Builds SQL strings.

/// A SELECT under construction.
pub struct Query { pub table: String, pub filters: Vec<String> }

impl Query {
    pub fn new(table: &str) -> Self { Self { table: table.into(), filters: vec![] } }
    pub fn filter(mut self, f: &str) -> Self { self.filters.push(f.into()); self }
    pub fn to_sql(&self) -> String {
        let mut sql = format!("SELECT * FROM {}", self.table);
        if !self.filters.is_empty() { sql += &format!(" WHERE {}", self.filters.join(" AND ")); }
        sql
    }
}
