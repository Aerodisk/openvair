///! Модуль работы с файлами requirements.txt для Python
///!
///! See also [`PythonRequirements`]
use std::{ops::Deref, str::FromStr};

#[derive(Clone, Debug, Default)]
pub struct PythonRequirements(pub Vec<RequirementRecord>);

impl PythonRequirements {
    pub fn get_version(&self, package_name: impl AsRef<str>) -> Option<&str> {
        for pkg in self.iter() {
            if pkg.package.as_str() == package_name.as_ref() {
                return Some(&pkg.version);
            }
        }

        None
    }

    pub fn from_file(path: &str) -> anyhow::Result<Self> {
        let contents = std::fs::read_to_string(path)?;
        Ok(Self::from_str(&contents)?)
    }
}

impl FromStr for PythonRequirements {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut res = Vec::new();

        for rec in s
            .trim()
            .split_whitespace()
            .map(|v| RequirementRecord::from_str(v))
        {
            if let Ok(r) = rec {
                res.push(r);
            } else {
                anyhow::bail!("failed to parse requirements file");
            }
        }

        Ok(Self(res))
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RequirementRecord {
    package: String,
    version: String,
}

impl FromStr for RequirementRecord {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let v = s.trim().split_terminator("==").collect::<Vec<_>>();
        if v.len() != 2 {
            anyhow::bail!("wrong format for python requirement: '{s}'");
        }
        let name = v[0];
        let version = v[1];

        Ok(RequirementRecord {
            package: name.to_string(),
            version: version.to_string(),
        })
    }
}

impl Deref for PythonRequirements {
    type Target = Vec<RequirementRecord>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

#[cfg(test)]
mod tests {
    use std::str::FromStr;

    use crate::openvair_manager::python::requirements::{PythonRequirements, RequirementRecord};

    #[test]
    fn test_deserialize_requirement_record() -> anyhow::Result<()> {
        let s = "test-pkg==1.0.1";
        let r = RequirementRecord::from_str(s)?;
        assert_eq!(
            r,
            RequirementRecord {
                package: "test-pkg".into(),
                version: "1.0.1".into()
            }
        );
        Ok(())
    }

    #[test]
    fn test_deserialize_requirements() -> anyhow::Result<()> {
        let s = "foo==1.0.1\n\
                       bar==2.3.1";
        let r = PythonRequirements::from_str(s)?;
        assert_eq!(r.len(), 2);
        assert!(r.contains(&RequirementRecord {
            package: "foo".into(),
            version: "1.0.1".into()
        }));
        assert!(r.contains(&RequirementRecord {
            package: "bar".into(),
            version: "2.3.1".into()
        }));
        Ok(())
    }

    #[test]
    fn test_requirements_get_version() -> anyhow::Result<()> {
        let s = "foo==1.0.1\n\
                       bar==2.3.1";
        let r = PythonRequirements::from_str(s)?;
        assert_eq!(r.get_version("foo"), Some("1.0.1".into()));
        Ok(())
    }
}
