export type VerificationStatus =
  | 'VERIFIED'
  | 'CONSISTENT'
  | 'NEEDS_REVIEW'
  | 'INCONSISTENT'
  | 'AMBIGUOUS'
  | 'UNABLE_TO_VERIFY';

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface GeocodingResult {
  coordinates: Coordinates;
  display_name: string;
  source: string;
  confidence: number;
  match_level?: string;
}

export interface TransformationStep {
  field: string;
  original_value: string;
  transformed_value: string;
  rule_applied: string;
}

export interface NormalizedAddress {
  original_input: string;
  normalized_text: string;
  locality?: string;
  subdistrict?: string;
  city?: string;
  district?: string;
  state?: string;
  state_code?: string;
  pincode?: string;
  detected_script?: string;
  transformations: TransformationStep[];
}

export interface ParsedAddress {
  premise?: string;
  locality?: string;
  subdistrict?: string;
  city?: string;
  district?: string;
  state?: string;
  state_code?: string;
  pincode?: string;
  landmarks: string[];
  unparsed_tokens: string[];
  detected_script?: string;
  parse_confidence: number;
}

export interface AddressScores {
  geographic_consistency: number;
  address_completeness: number;
  entity_match: number;
}

export interface CandidateEntity {
  id: string;
  name: string;
  name_hi?: string;
  name_mr?: string;
  entity_type: string;
  state?: string;
  state_code?: string;
  district?: string;
  subdistrict?: string;
  pincode?: string;
  coordinates?: Coordinates;
  similarity_score?: number;
  match_source?: string;
}

export interface EntityMatchBreakdown {
  name_similarity: number;
  admin_context: number;
  pin_compatibility: number;
  geographic_proximity: number;
  entity_type_weight: number;
  total_score: number;
}

export interface EntityMatchResult {
  candidate: CandidateEntity;
  match_score: number;
  breakdown: EntityMatchBreakdown;
  match_confidence: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface AmbiguityDetails {
  is_ambiguous: boolean;
  top_candidates: EntityMatchResult[];
  ambiguity_reason?: string;
  suggested_disambiguations: string[];
}

export interface CompletenessCriteria {
  has_premise: boolean;
  has_road: boolean;
  has_landmark: boolean;
  has_locality: boolean;
  has_subdistrict: boolean;
  has_district: boolean;
  has_state: boolean;
  has_pincode: boolean;
}

export interface CompletenessResult {
  score: number;
  rating: 'COMPLETE' | 'ADEQUATE' | 'PARTIAL' | 'MINIMAL';
  criteria: CompletenessCriteria;
  missing_fields: string[];
  breakdown: Record<string, number>;
}

export interface EvidenceNode {
  id: string;
  label: string;
  node_type: string;
  level: string;
  status: 'VERIFIED' | 'WARNING' | 'CONFLICT' | 'UNVERIFIED';
  properties?: Record<string, any>;
}

export interface EvidenceEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  label: string;
  severity: 'INFO' | 'WARNING' | 'CONFLICT';
  passed: boolean;
  evidence_text?: string;
}

export interface EvidenceGraphResponse {
  nodes: EvidenceNode[];
  relationships: EvidenceEdge[];
  summary: string;
  conflicts_count: number;
  warnings_count: number;
}

export interface HierarchyNode {
  level: string;
  name: string;
  canonical_name?: string;
  level_code?: string;
  matched: boolean;
  evidence?: string;
}

export interface AdministrativeHierarchyResult {
  country: string;
  state?: string;
  state_code?: string;
  district?: string;
  subdistrict?: string;
  locality?: string;
  is_consistent: boolean;
  hierarchy_chain: HierarchyNode[];
  mismatch_details: string[];
}

export interface BoundaryVerificationResult {
  point_inside_state: boolean;
  point_inside_district: boolean;
  point_inside_subdistrict?: boolean;
  point_inside_locality?: boolean;
  detected_state?: string;
  detected_district?: string;
  detected_subdistrict?: string;
  detected_locality?: string;
  boundary_geojson?: any;
}

export interface PinVerificationResult {
  pincode?: string;
  is_valid_format: boolean;
  matched: boolean;
  matched_post_offices: string[];
  matched_district?: string;
  matched_state?: string;
  pin_centroid?: Coordinates;
  distance_to_coordinates_km?: number;
  evidence: string;
}

export interface ScoreBreakdown {
  hierarchy_score: number;
  hierarchy_max: number;
  boundary_score: number;
  boundary_max: number;
  locality_score: number;
  locality_max: number;
  pincode_score: number;
  pincode_max: number;
  geocoding_score: number;
  geocoding_max: number;
  nearby_score: number;
  nearby_max: number;
  total_score: number;
}

export interface EvidenceItem {
  code: string;
  category: string;
  passed: boolean;
  status: 'PASSED' | 'FAILED' | 'WARNING' | 'SKIPPED';
  weight: number;
  score_contribution: number;
  title: string;
  description: string;
}

export interface NearbyPlace {
  name: string;
  category: string;
  subtype?: string;
  distance_km: number;
  coordinates: Coordinates;
  address?: string;
  district?: string;
  state?: string;
}

export interface DataSourceAttribution {
  name: string;
  source_url: string;
  license: string;
  version: string;
  coverage: string;
}

export interface VerificationResponse {
  verification_id: string;
  timestamp: string;
  status: VerificationStatus;
  score: number;
  summary: string;
  explanation: string[];
  warnings: string[];
  evidence: EvidenceItem[];
  normalized_address: NormalizedAddress;
  parsed_address: ParsedAddress;
  geocoding?: GeocodingResult;
  administrative_hierarchy: AdministrativeHierarchyResult;
  boundary_verification: BoundaryVerificationResult;
  pin_verification: PinVerificationResult;
  score_breakdown: ScoreBreakdown;
  nearby_places: NearbyPlace[];
  data_sources?: DataSourceAttribution[];
  scores?: AddressScores;
  ambiguity?: AmbiguityDetails;
  completeness?: CompletenessResult;
  candidate_matches?: EntityMatchResult[];
  evidence_graph?: EvidenceGraphResponse;
}

export interface StructuredAddressRequest {
  address_line?: string;
  locality?: string;
  subdistrict?: string;
  city?: string;
  district?: string;
  state?: string;
  pincode?: string;
}

export interface VerificationRequest {
  address?: string;
  structured?: StructuredAddressRequest;
  radius_km?: number;
  include_geojson?: boolean;
}
