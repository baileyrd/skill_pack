//! Pure-string POSIX path manipulation, matching Python's `posixpath`.

/// Final component of `path` (`posixpath.basename`).
pub fn basename(path: &str) -> &str {
    path.rsplit('/').next().unwrap_or("")
}

/// Everything before the final slash (`posixpath.dirname`).
pub fn dirname(path: &str) -> &str {
    match path.rfind('/') {
        Some(0) => "/",
        Some(i) => path[..i].trim_end_matches('/'),
        None => "",
    }
}

/// Join components; an absolute component resets the result (`posixpath.join`).
pub fn join(parts: &[&str]) -> String {
    let mut out = String::new();
    for p in parts {
        if p.starts_with('/') {
            out = p.to_string();
        } else if out.is_empty() || out.ends_with('/') {
            out.push_str(p);
        } else {
            out.push('/');
            out.push_str(p);
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn basics() {
        assert_eq!(basename("/a/b.txt"), "b.txt");
        assert_eq!(dirname("/a/b.txt"), "/a");
        assert_eq!(join(&["a", "/b", "c"]), "/b/c");
    }
}
