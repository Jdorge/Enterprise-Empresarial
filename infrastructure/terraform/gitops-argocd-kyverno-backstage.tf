terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.11.0"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
  }
}

resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = "7.3.9"
  namespace        = "argocd"
  create_namespace = true

  values = []
}

resource "helm_release" "argocd_rollouts" {
  name             = "argo-rollouts"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-rollouts"
  version          = "2.37.1"
  namespace        = "argo-rollouts"
  create_namespace = true

  values = []
}

resource "kubectl_manifest" "kyverno_crds" {
  yaml_body = <<-YAML
apiVersion: v1
kind: List
items:
- apiVersion: apiextensions.k8s.io/v1
  kind: CustomResourceDefinition
  metadata:
    name: placeholder-kyverno-crd
YAML
}

resource "helm_release" "kyverno" {
  name             = "kyverno"
  repository       = "https://kyverno.github.io/kyverno"
  chart            = "kyverno"
  version          = "3.2.3"
  namespace        = "kyverno"
  create_namespace = true

  depends_on = [kubectl_manifest.kyverno_crds]

  values = []
}

resource "helm_release" "schema_registry" {
  name             = "schema-registry"
  repository       = "https://charts.bitnami.com/bitnami"
  chart            = "schema-registry"
  version          = "18.1.3"
  namespace        = "enterprise"
  create_namespace = false

  values = []
}

resource "helm_release" "backstage" {
  name             = "backstage"
  repository       = "https://backstage.github.io/charts"
  chart            = "backstage"
  version          = "1.34.1"
  namespace        = "backstage"
  create_namespace = true

  values = []
}
