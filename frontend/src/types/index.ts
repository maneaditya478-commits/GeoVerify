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
  channels?: string[];
}

export interface AppliedPenalty {
  name: string;
  deduction: number;
  reason: string;
}

export interface RankingExplanation {
  feature_contributions?: Record<string, number>;
  applied_penalties?: AppliedPenalty[];
  total_penalty_deduction?: number;
  retrieval_channels?: string[];
  consensus_count?: number;
  rank?: number;
  score_delta_to_next?: number;
  admin_differences?: string[];
  summary?: string;
}

export interface EntityMatchBreakdown {
  name_similarity: number;
  admin_context: number;
  parent_child_compatibility?: number;
  pin_compatibility: number;
  geographic_proximity: number;
  transliteration_phonetic?: number;
  entity_type_weight: number;
  retrieval_consensus?: number;
  data_quality?: number;
  penalty_deduction?: number;
  total_score: number;
}

export interface EntityMatchResult {
  candidate: CandidateEntity;
  match_score: number;
  breakdown: EntityMatchBreakdown;
  match_confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  ranking_explanation?: RankingExplanation;
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

// -------------------------------------------------------------
// Phase 7: Document & OCR Verification Types
// -------------------------------------------------------------

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  page_num?: number;
}

export interface OCRWord {
  text: string;
  confidence: number;
  bbox?: BoundingBox;
  line_num?: number;
  word_num?: number;
  page_num?: number;
}

export interface OCRLine {
  text: string;
  confidence: number;
  words?: OCRWord[];
  bbox?: BoundingBox;
  line_num?: number;
}

export interface OCRBlock {
  text: string;
  confidence: number;
  lines?: OCRLine[];
  bbox?: BoundingBox;
}

export interface OCRPage {
  page_num: number;
  width: number;
  height: number;
  text: string;
  confidence: number;
  blocks: OCRBlock[];
  lines: OCRLine[];
  words: OCRWord[];
  detected_languages: Record<string, number>;
  processing_time_ms: number;
}

export interface OCRResult {
  document_id: string;
  engine: string;
  pages: OCRPage[];
  full_text: string;
  mean_confidence: number;
  primary_language: string;
  quality_status: 'HIGH' | 'MEDIUM' | 'LOW' | 'FAILED';
  processing_time_ms: number;
}

export interface ExtractedAddressField {
  field_name: string;
  raw_value: string;
  normalized_value?: string;
  confidence: number;
  line_num?: number;
  page_num?: number;
  bbox?: BoundingBox;
  source_text?: string;
  correction_reason?: string;
}

export interface ExtractedAddressCandidate {
  candidate_id: string;
  address_type: string;
  raw_address_text: string;
  assembled_address: string;
  fields: Record<string, ExtractedAddressField>;
  structured_components: Record<string, string | null>;
  extraction_confidence: number;
  extraction_status: 'EXTRACTED' | 'PARTIAL' | 'PARTIALLY_EXTRACTED' | 'AMBIGUOUS' | 'NOT_FOUND' | 'FAILED';
  page_num: number;
  region_bbox?: BoundingBox;
  provenance: Record<string, any>;
  pin_recovered: boolean;
  verification_result?: VerificationResponse;
}

export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: string;
  mime_type: string;
  size_bytes: number;
  page_count: number;
  sha256: string;
}

export interface OCRMetadata {
  status: string;
  engine: string;
  mean_confidence: number;
  quality_status: 'HIGH' | 'MEDIUM' | 'LOW' | 'FAILED';
  primary_language: string;
  languages_detected: Record<string, number>;
  pages_processed: number;
  processing_time_ms: number;
  ocr_result?: OCRResult;
}

export interface AddressExtractionMetadata {
  status: string;
  extraction_confidence: number;
  total_candidates_found: number;
  selected_candidate_index: number;
  extracted_fields_count: number;
  pin_recovered: boolean;
  processing_time_ms: number;
}

export interface DocumentVerificationResponse {
  document: DocumentMetadata;
  ocr: OCRMetadata;
  address_extraction: AddressExtractionMetadata;
  address_candidates: ExtractedAddressCandidate[];
  primary_candidate?: ExtractedAddressCandidate;
  verification?: VerificationResponse;
  transformation_pipeline: Array<Record<string, any>>;
  stage_timings_ms: Record<string, number>;
  summary: string;
}
