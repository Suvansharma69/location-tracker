import phonenumbers
from phonenumbers import timezone, geocoder, carrier, number_type, PhoneNumberType, NumberParseException

# Enter phone number along with country code
number = input("Enter phone number with country code: ")

try:
    # Parsing the phone number
    phone_number = phonenumbers.parse(number)

    # Validate phone number
    if not phonenumbers.is_valid_number(phone_number):
        print("Invalid phone number! Please enter a valid number.")
    else:
        # Time Zone(s)
        time_zone = timezone.time_zones_for_number(phone_number)
        print(f"Time Zone(s): {time_zone}")

        # General Location (Country / Region)
        location = geocoder.description_for_number(phone_number, "en")
        print(f"General Location: {location}")

        # Service Provider
        service = carrier.name_for_number(phone_number, "en")
        print(f"Service Provider: {service}")

        # Phone Number Type
        phone_type = number_type(phone_number)
        type_mapping = {
            PhoneNumberType.MOBILE: "Mobile",
            PhoneNumberType.FIXED_LINE: "Fixed-line",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed-line or Mobile",
            PhoneNumberType.TOLL_FREE: "Toll-Free",
            PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            PhoneNumberType.VOIP: "VoIP",
            PhoneNumberType.PAGER: "Pager",
            PhoneNumberType.UAN: "UAN (Universal Access Number)",
            PhoneNumberType.UNKNOWN: "Unknown",
        }
        print(f"Number Type: {type_mapping.get(phone_type, 'Unknown')}")

        # Carrier Network Code (if available)
        network_code = carrier._is_mobile(phone_number)
        print(f"Network Code: {network_code}")

        # Format Number
        int_format = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        nat_format = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        e164_format = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        print(f"International Format: {int_format}")
        print(f"National Format: {nat_format}")
        print(f"E.164 Format: {e164_format}")

        # Country Code & Name
        country_code = phone_number.country_code
        country_name = geocoder.country_name_for_number(phone_number, "en")
        print(f"Country Code: +{country_code}")
        print(f"Country Name: {country_name}")

        # Possible Lengths
        possible_lengths = phonenumbers.length_of_geographical_area_code(phone_number)
        print(f"Possible Lengths: {possible_lengths}")

        # Checking if the number is reachable
        is_possible = phonenumbers.is_possible_number(phone_number)
        is_valid = phonenumbers.is_valid_number(phone_number)
        print(f"Is Possible Number? {'Yes' if is_possible else 'No'}")
        print(f"Is Valid Number? {'Yes' if is_valid else 'No'}")

except NumberParseException:
    print("Invalid phone number format. Please try again.")
